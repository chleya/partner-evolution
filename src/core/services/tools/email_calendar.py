"""
Partner-Evolution 邮件/日历集成模块
Gmail + Google Calendar API
"""
import os
import sys
import datetime
from typing import Dict, List, Optional
from pathlib import Path

# 尝试导入Google API
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


class EmailClient:
    """邮件客户端"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or "credentials.json"
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def authenticate(self) -> bool:
        """认证"""
        if not GOOGLE_API_AVAILABLE:
            return False
        
        try:
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"认证失败: {e}")
            return False
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """获取未读邮件"""
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': msg_data.get('snippet', '')
                })
            
            return emails
        except Exception as e:
            print(f"获取邮件失败: {e}")
            return []
    
    def get_today_emails(self) -> List[Dict]:
        """获取今天的邮件"""
        if not self.service:
            return []
        
        try:
            today = datetime.datetime.now().strftime('%Y/%m/%d')
            results = self.service.users().messages().list(
                userId='me',
                q=f'after:{today}',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            return len(messages)
        except:
            return 0


class CalendarClient:
    """日历客户端"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or "credentials.json"
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def authenticate(self) -> bool:
        """认证"""
        if not GOOGLE_API_AVAILABLE:
            return False
        
        try:
            creds = None
            if os.path.exists('calendar_token.json'):
                creds = Credentials.from_authorized_user_file('calendar_token.json', self.scopes)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                with open('calendar_token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"日历认证失败: {e}")
            return False
    
    def get_today_events(self) -> List[Dict]:
        """获取今天的事件"""
        if not self.service:
            return []
        
        try:
            now = datetime.datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            events_result = self.service.events().list(
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
        if not self.service:
            return []
        
        try:
            now = datetime.datetime.utcnow()
            future = now + datetime.timedelta(days=days)
            
            events_result = self.service.events().list(
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


class WorkFlowAssistant:
    """工作流助手 - 整合邮件和日历"""
    
    def __init__(self):
        self.email_client = EmailClient()
        self.calendar_client = CalendarClient()
    
    def get_daily_summary(self) -> Dict:
        """获取每日摘要"""
        summary = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "emails": {
                "unread": 0,
                "today": 0,
                "important": []
            },
            "calendar": {
                "today_events": [],
                "upcoming": []
            },
            "suggestions": []
        }
        
        # 邮件
        if self.email_client.authenticate():
            summary["emails"]["unread"] = len(self.email_client.get_unread_emails(5))
            summary["emails"]["today"] = self.email_client.get_today_emails()
        
        # 日历
        if self.calendar_client.authenticate():
            summary["calendar"]["today_events"] = self.calendar_client.get_today_events()
            summary["calendar"]["upcoming"] = self.calendar_client.get_upcoming_events(7)
        
        # 生成建议
        if summary["calendar"]["today_events"]:
            summary["suggestions"].append(f"今天有 {len(summary['calendar']['today_events'])} 个会议")
        else:
            summary["suggestions"].append("今天没有会议，可以专注工作")
        
        if summary["emails"]["unread"] > 10:
            summary["suggestions"].append(f"有 {summary['emails']['unread']} 封未读邮件，建议先处理")
        
        return summary
    
    def generate_report(self) -> str:
        """生成报告"""
        summary = self.get_daily_summary()
        
        report = f"""
# 📋 每日工作摘要 - {summary['date']}

## 📧 邮件
- 未读邮件: {summary['emails']['unread']} 封
- 今日新邮件: {summary['emails']['today']} 封

## 📅 日程
"""
        
        if summary['calendar']['today_events']:
            report += "### 今日会议\n"
            for event in summary['calendar']['today_events']:
                report += f"- **{event['start'][11:16]}** - {event['summary']}\n"
        else:
            report += "今日无会议安排\n"
        
        report += "\n## 💡 建议\n"
        for suggestion in summary['suggestions']:
            report += f"- {suggestion}\n"
        
        return report


# 模拟版本（不依赖Google API）
class MockWorkFlow:
    """模拟工作流（不需API）"""
    
    @staticmethod
    def get_daily_summary() -> Dict:
        now = datetime.datetime.now()
        return {
            "date": now.strftime("%Y-%m-%d"),
            "emails": {
                "unread": 5,
                "today": 12,
                "important": [
                    {"subject": "项目进度更新", "sender": "team@company.com"},
                    {"subject": "会议邀请", "sender": "boss@company.com"}
                ]
            },
            "calendar": {
                "today_events": [
                    {"summary": "团队周会", "start": "10:00", "end": "11:00"},
                    {"summary": "代码审查", "start": "14:00", "end": "15:00"},
                    {"summary": "1对1沟通", "start": "16:00", "end": "16:30"}
                ],
                "upcoming": [
                    {"summary": "周五汇报", "start": "2026-03-07 10:00"}
                ]
            },
            "suggestions": [
                "今天有3个会议，建议提前准备",
                "有重要邮件需要处理",
                "上午适合做深度工作"
            ]
        }


# 测试
if __name__ == "__main__":
    print("=== 工作流助手测试 ===")
    
    workflow = MockWorkFlow()
    summary = workflow.get_daily_summary()
    
    print(f"日期: {summary['date']}")
    print(f"未读邮件: {summary['emails']['unread']}")
    print(f"今日会议: {len(summary['calendar']['today_events'])}")
    print("\n建议:")
    for s in summary['suggestions']:
        print(f"  - {s}")
