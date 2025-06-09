export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isTyping?: boolean
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface SendMessageRequest {
  message: string
  sessionId?: string
}

export interface SendMessageResponse {
  message: ChatMessage
  sessionId: string
}

// Abstract API interface for easy replacement
export interface ChatAPI {
  sendMessage(request: SendMessageRequest): Promise<SendMessageResponse>
  getSession(sessionId: string): Promise<ChatSession>
  createSession(): Promise<ChatSession>
  getSessions(): Promise<ChatSession[]>
}

// Mock implementation
class MockChatAPI implements ChatAPI {
  private sessions: Map<string, ChatSession> = new Map()
  private messageCounter = 0

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  private generateMessageId(): string {
    return `msg-${++this.messageCounter}`
  }

  // Mock responses for different types of administrative queries
  private getMockResponse(userMessage: string): string {
    const message = userMessage.toLowerCase()

    if (message.includes('学籍') || message.includes('注册')) {
      return '根据学校规定，学籍注册需要在每学期开学后两周内完成。您需要准备以下材料：1) 身份证原件及复印件；2) 录取通知书；3) 户口本或户籍证明；4) 一寸免冠照片2张。如需了解具体办理流程，请携带相关材料到学生事务中心二楼注册处办理。'
    }

    if (message.includes('成绩') || message.includes('查询')) {
      return '您可以通过以下方式查询成绩：1) 登录学校教务系统（jwc.ruc.edu.cn）；2) 使用学号和密码登录；3) 在"成绩查询"模块查看各科成绩。如遇到登录问题，请联系教务处技术支持（电话：010-62511122）或携带学生证到教务处现场咨询。'
    }

    if (message.includes('奖学金') || message.includes('助学金')) {
      return '奖学金评定每学年进行一次，通常在9-10月份开始申请。评定标准包括：1) 学习成绩（占60%）；2) 综合素质评价（占30%）；3) 社会实践和创新能力（占10%）。助学金申请需要提供家庭经济困难证明，具体申请流程请关注学生资助中心通知。'
    }

    if (message.includes('选课') || message.includes('课程')) {
      return '选课系统通常在每学期末开放，用于下学期的课程选择。选课时间分为预选阶段和正选阶段：1) 预选阶段：可以选择所有开放课程；2) 正选阶段：根据预选结果进行调整。请注意选课时间限制，逾期无法修改。如有课程冲突或特殊需求，请联系所在院系教务员。'
    }

    if (message.includes('宿舍') || message.includes('住宿')) {
      return '宿舍分配按照学院和年级统一安排。新生入学后统一分配宿舍，老生可在规定时间内申请调换。宿舍管理相关事宜请联系：1) 宿舍管理中心（学生公寓一楼）；2) 各楼层宿管员；3) 学生事务中心住宿管理科。违规用电、晚归等问题会影响住宿评价。'
    }

    if (message.includes('图书馆') || message.includes('借书')) {
      return '图书馆开放时间：周一至周日 8:00-22:00。借书流程：1) 使用校园卡在自助借还机或人工柜台借书；2) 本科生可借图书20册，研究生30册；3) 借期为30天，可续借2次。如需预约图书、研讨间或有其他问题，可使用图书馆APP或到咨询台寻求帮助。'
    }

    if (message.includes('毕业') || message.includes('学位')) {
      return '毕业申请需要满足以下条件：1) 完成培养方案规定的所有课程学习；2) 学分达到毕业要求；3) 完成毕业论文并通过答辩；4) 无违纪处分记录。学位授予需要满足学位条例规定的标准。具体申请流程请关注教务处和研究生院的通知。'
    }

    // Default response
    return '感谢您的咨询。作为人大智慧行政助手，我可以帮您解答学籍管理、成绩查询、奖助学金、选课系统、住宿安排、图书借阅、毕业学位等相关问题。请您详细描述您需要了解的具体问题，我会为您提供准确的政策解读和办事指南。'
  }

  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

    let session: ChatSession

    if (request.sessionId && this.sessions.has(request.sessionId)) {
      session = this.sessions.get(request.sessionId)!
    } else {
      session = await this.createSession()
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: this.generateMessageId(),
      role: 'user',
      content: request.message,
      timestamp: new Date(),
    }

    session.messages.push(userMessage)

    // Generate assistant response
    const assistantMessage: ChatMessage = {
      id: this.generateMessageId(),
      role: 'assistant',
      content: this.getMockResponse(request.message),
      timestamp: new Date(),
    }

    session.messages.push(assistantMessage)
    session.updatedAt = new Date()

    // Update session title based on first message
    if (session.messages.length === 2) {
      session.title = request.message.slice(0, 20) + (request.message.length > 20 ? '...' : '')
    }

    this.sessions.set(session.id, session)

    return {
      message: assistantMessage,
      sessionId: session.id,
    }
  }

  async getSession(sessionId: string): Promise<ChatSession> {
    const session = this.sessions.get(sessionId)
    if (!session) {
      throw new Error('Session not found')
    }
    return session
  }

  async createSession(): Promise<ChatSession> {
    const session: ChatSession = {
      id: this.generateId(),
      title: '新对话',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    this.sessions.set(session.id, session)
    return session
  }

  async getSessions(): Promise<ChatSession[]> {
    return Array.from(this.sessions.values()).sort(
      (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime(),
    )
  }
}

// Export singleton instance
export const chatAPI: ChatAPI = new MockChatAPI()
