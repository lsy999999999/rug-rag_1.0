# 文件路径: /backend/wenshu/processors/form_filler.py

import json
from typing import Any, Dict, List

from docx import Document
from llama_index.core.llms.llm import LLM
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.prompts import PromptTemplate
from pydantic import BaseModel, Field


# Pydantic模型保持不变，因为它已经足够精确
class FillingInstruction(BaseModel):
    table_index: int = Field(..., description="The 0-based index of the target table in the document.")
    row: int = Field(..., description="The 0-based row index of the target cell.")
    col: int = Field(..., description="The 0-based column index of the target cell.")
    value: str = Field(..., description="The string value to fill into the cell.")
    reason: str = Field(..., description="A brief explanation of why this location was chosen.")

class AutofillAnalysis(BaseModel):
    filling_instructions: List[FillingInstruction] = Field(
        default_factory=list, description="A list of precise instructions to fill the form cells."
    )
    summary: str = Field(..., description="A summary of what was filled and what could not be filled.")


class DocxFormFiller:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.document: Document | None = None

    def load_document(self, doc_path_or_obj: Any):
        is_document_object = hasattr(doc_path_or_obj, "paragraphs") and hasattr(doc_path_or_obj, "tables")
        if is_document_object:
            self.document = doc_path_or_obj
        else:
            self.document = Document(doc_path_or_obj)

    # --- START: FINAL, IMPROVED METHOD ---
    # This method now extracts ALL cells, marking empty ones, as inspired by your reference.
    def _extract_table_structures(self) -> List[Dict]:
        """Extracts complete structure from all tables, including empty cells."""
        if not self.document:
            return []
        
        structures = []
        for table_idx, table in enumerate(self.document.tables):
            structure = {
                'table_index': table_idx,
                'dimensions': f"{len(table.rows)}x{len(table.columns)}",
                'cells': []
            }
            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    structure['cells'].append({
                        'position': f"[{row_idx},{col_idx}]",
                        'text': cell_text,
                        'is_empty': not bool(cell_text) # Mark if the cell is empty
                    })
            structures.append(structure)
        return structures
    # --- END: FINAL, IMPROVED METHOD ---

    async def _run_llm_program(self, prompt_template_str: str, **kwargs: Any) -> Dict[str, Any]:
        program = LLMTextCompletionProgram.from_defaults(
            output_parser=PydanticOutputParser(output_cls=AutofillAnalysis),
            prompt=PromptTemplate(prompt_template_str),
            llm=self.llm,
            verbose=True,
        )
        try:
            response: AutofillAnalysis = await program.acall(**kwargs)
            return response.model_dump()
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error during LLM call or JSON parsing: {e}")
            return {"filling_instructions": [], "summary": f"Failed due to error: {e}"}

    # --- START: FINAL, IMPROVED PROMPT in a shared method ---
    async def _get_filling_analysis(self, instruction_source: Dict[str, str]) -> Dict[str, Any]:
        """A single, powerful method to get filling analysis for any instruction type."""
        table_structures = self._extract_table_structures()
        
        # Determine if the instruction is from context or feedback
        instruction_key = list(instruction_source.keys())[0] # "context" or "feedback"
        instruction_value = instruction_source[instruction_key]

        # This is the new, much more precise prompt
        prompt = (
            "You are a hyper-attentive data entry assistant. Your only job is to precisely map user information to the correct empty cell in a table.\n\n"
            "## The Input You Receive:\n"
            "1.  **Table Structures**: A JSON object describing all tables. It includes every cell's coordinate `[row,col]`, its text, and an `is_empty` flag.\n"
            "2.  **User Instruction**: A piece of text containing the information to be filled.\n\n"
            "## Your Step-by-Step Task:\n"
            "1.  **Extract Key-Value Pairs**: Read the user instruction. For '我的姓名是lsy，性别为女', extract `{'姓名': 'lsy', '性别': '女'}`.\n"
            "2.  **Locate the Label Cell**: For each key (e.g., '姓名'), scan through the `Table Structures` to find the exact cell that contains this text.\n"
            "3.  **Locate the Target Cell**: Once you find the label cell (e.g., at `[1,1]`), find the adjacent **empty** cell (`is_empty: true`). This is almost always the cell to the immediate right (e.g., `[1,2]`).\n"
            "4.  **Construct Instructions**: Create a JSON instruction for each key-value pair, using the coordinates of the **target empty cell** you found in step 3.\n\n"
            "## Table Structures:\n"
            "```json\n{table_structures_json}\n```\n\n"
            "## User Instruction:\n"
            "```text\n{instruction}\n```\n\n"
            "Now, perform your task and return ONLY the JSON object with the filling instructions."
        )

        return await self._run_llm_program(
            prompt,
            table_structures_json=json.dumps(table_structures, ensure_ascii=False, indent=2),
            instruction=instruction_value
        )
    # --- END: FINAL, IMPROVED PROMPT ---

    async def analyze_for_autofill(self, context: str) -> Dict[str, Any]:
        return await self._get_filling_analysis({"context": context})

    async def refine_with_feedback(self, feedback: str) -> Dict[str, Any]:
        return await self._get_filling_analysis({"feedback": feedback})

    # --- START: FINAL, IMPROVED apply_instructions ---
    def apply_instructions(self, instructions: List[Dict[str, Any]]):
        """Applies instructions with robust cell handling, inspired by reference code."""
        if not self.document:
            print("✗ Cannot apply instructions: Document not loaded.")
            return

        for instruction in instructions:
            try:
                table_idx = int(instruction.get("table_index", -1))
                row = int(instruction.get("row", -1))
                col = int(instruction.get("col", -1))
                value = str(instruction.get("value", ""))

                if table_idx < 0 or row < 0 or col < 0:
                    continue
                
                table = self.document.tables[table_idx]
                cell = table.cell(row, col)

                # Smart filling: if the cell already contains a label with a separator,
                # append the value. Otherwise, overwrite. This handles cases like "姓名：[___]".
                current_text = cell.text.strip()
                separators = ['：', ':']
                handled = False
                for sep in separators:
                    if sep in current_text:
                        cell.text = f"{current_text}{value}"
                        handled = True
                        break
                
                if not handled:
                    # If no separator, or cell is empty, just set the text.
                    cell.text = value
                
                print(f"✓ Filled '{value}' in Table {table_idx}, Cell [{row},{col}]")

            except (IndexError, ValueError, Exception) as e:
                print(f"✗ Failed to apply instruction {instruction}: {e}")
    # --- END: FINAL, IMPROVEMENTS ---