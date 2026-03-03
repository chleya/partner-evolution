"""
Partner-Evolution - Google邮件/日历真实集成
OAuth2授权 + 真实API调用
"""
import os
import datetime
from typing import List, Dict, Optional

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# ==================== 配置 ====================
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'


class GoogleIntegration:
    """Google邮件/日历集成"""
    
    def __init__(self):
        self.creds = None
        self.gmail_service = None
        self.calendar_service = None
        self.authenticated = False
    
    def authenticate(self, credentials_path: str = None) -> bool:
        """OAuth2认证"""
        if not GOOGLE_API_AVAILABLE:
            print("Google API not available")
            return False
        
        creds_file = credentials_path or CREDENTIALS_FILE
        
        # 加载已有token
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # 需要认证
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(creds_file):
                    print(f"请先下载OAuth凭证: https://console.cloud.google.com/")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 保存token
            with open(TOKEN_FILE, 'w') as f:
                f.write(self.creds.to_json())
        
        # 构建服务
        try:
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            self.authenticated = True
            return True
        except Exception as e:
            print(f"认证失败: {e}")
            return False
    
    # ==================== 邮件功能 ====================
    
    def get_emails(self, max_results: int = 10, query: str = '') -> List[Dict]:
        """获取邮件列表"""
        if not self.gmail_service:
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                msg_data = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                # 提取header
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg_data.get('snippet', '')
                })
            
            return emails
        except Exception as e:
            print(f"获取邮件失败: {e}")
            return []
    
    def get_unread_emails(self, max_results: int = 5) -> List[Dict]:
        """获取未读邮件"""
        return self.get_emails(max_results, query='is:unread')
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """发送邮件"""
        if not self.gmail_service:
            return False
        
        try:
            from email.mime.text import MIMEText
            import base64
            
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            
            encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': encoded}
            ).execute()
            
            return True
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    # ==================== 日历功能 ====================
    
    def get_today_events(self) -> List[Dict]:
        """获取今日事件"""
        if not self.calendar_service:
            return []
        
        try:
            now = datetime.datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [{
                'summary': e.get('summary', '无标题'),
                'start': e['start'].get('dateTime', e['start'].get('date')),
                'end': e['end'].get('dateTime', e['end'].get('date')),
                'location': e.get('location', ''),
                'description': e.get('description', '')
            } for e in events]
        except Exception as e:
            print(f"获取日历失败: {e}")
            return []
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """获取接下来几天的事件"""
        if not self.calendar_service:
            return []
        
        try:
            now = datetime.datetime.utcnow()
            future = now + datetime.timedelta(days=days)
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=future.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime',
                maxResults=20
            ).execute()
            
            events = events_result.get('items', [])
            
            return [{
                'summary': e.get('summary', '无标题'),
                'start': e['start'].get('dateTime', e['start'].get('date')),
                'end': e['end'].get('dateTime', e['end'].get('date')),
            } for e in events]
        except:
            return []
    
    def create_event(self, title: str, start_time: datetime.datetime, 
                     end_time: datetime.datetime, description: str = '') -> bool:
        """创建日历事件"""
        if not self.calendar_service:
            return False
        
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {'dateTime': start_time.isoformat()},
                'end': {'dateTime': end_time.isoformat()}
            }
            
            self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return True
        except Exception as e:
            print(f"创建事件失败: {e}")
            return False
    
    # ==================== 智能功能 ====================
    
    def generate_daily_briefing(self) -> str:
        """生成每日简报"""
        # 获取数据
        unread = self.get_unread_emails(5)
        today_events = self.get_today_events()
        
        # 生成报告
        briefing = f"""
# ☀️ 今日工作简报

## 📧 邮件
- 未读邮件: {len(unread)} 封
"""
        
        if unread:
            briefing += "- **重要邮件:**\n"
            for e in unread[:3]:
                briefing += f"  - {e['subject'][:50]}\n"
        
        briefing += f"""
## 📅 日程
- 今日会议: {len(today_events)} 个
"""
        
        if today_events:
            briefing += "- **时间安排:**\n"
            for e in today_events[:3]:
                start = e['start'][11:16] if 'T' in e['start'] else e['start']
                briefing += f"  - {start} - {e['summary']}\n"
        
        return briefing


# ==================== Streamlit界面 ====================
def create_streamlit_app():
    """创建Streamlit界面"""
    import streamlit as st
    
    st.set_page_config(title="Partner-Evolution - Gmail/Calendar", page_icon="📧")
    st.title("📧 邮件 & 📅 日历集成")
    
    # 初始化
    google = GoogleIntegration()
    
    # 认证
    st.sidebar.header("🔐 Google授权")
    
    if st.sidebar.button("🔗 连接Google"):
        with st.spinner("认证中..."):
            if google.authenticate():
                st.sidebar.success("✅ 已连接!")
            else:
                st.sidebar.error("❌ 请先配置credentials.json")
    
    if google.authenticated:
        st.success("✅ 已连接到Google")
        
        # Tab
        tab1, tab2, tab3 = st.tabs(["📧 邮件", "📅 日历", "📊 早报"])
        
        with tab1:
            st.subheader("📧 邮件管理")
            
            # 未读邮件
            st.write("### 未读邮件")
            unread = google.get_unread_emails()
            
            if unread:
                for e in unread:
                    with st.expander(f"📬 {e['subject'][:50]}"):
                        st.write(f"**来自:** {e['sender']}")
                        st.write(f"**摘要:** {e['snippet']}")
            else:
                st.info("没有未读邮件")
            
            # 发送邮件
            st.write("### 发送邮件")
            to = st.text_input("收件人")
            subject = st.text_input("主题")
            body = st.text_area("内容")
            
            if st.button("发送") and to and subject:
                if google.send_email(to, subject, body):
                    st.success("发送成功!")
                else:
                    st.error("发送失败")
        
        with tab2:
            st.subheader("📅 日历")
            
            # 今日事件
            st.write("### 今日")
            events = google.get_today_events()
            
            if events:
                for e in events:
                    start = e['start'][11:16] if 'T' in e['start'] else e['start']
                    st.success(f"🕐 {start} - {e['summary']}")
            else:
                st.info("今天没有会议")
            
            # 创建事件
            st.write("### 创建事件")
            new_title = st.text_input("事件标题")
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("日期")
            with col2:
                new_time = st.time_input("时间")
            
            if st.button("创建") and new_title:
                start = datetime.datetime.combine(new_date, new_time)
                end = start + datetime.timedelta(hours=1)
                if google.create_event(new_title, start, end):
                    st.success("创建成功!")
                    st.rerun()
        
        with tab3:
            st.subheader("📊 AI早报")
            
            if st.button("生成今日简报"):
                with st.spinner("生成中..."):
                    briefing = google.generate_daily_briefing()
                    st.markdown(briefing)
    
    else:
        st.warning("⚠️ 请先在左侧点击'连接Google'")
        st.info("""
        ### 如何获取授权:
        1. 访问 Google Cloud Console
        2. 创建OAuth 2.0凭证
        3. 下载credentials.json到项目目录
        """)


if __name__ == '__main__':
    create_streamlit_app()
