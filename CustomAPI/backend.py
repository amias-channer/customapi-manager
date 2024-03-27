from .models import User, Api, Owner, Editor, Login
from .database import SessionLocal
from uuid import UUID, uuid4


class Backend:
    def __init__(self):
        self.db: Backend = SessionLocal()

    def login(self, username: str, password: str, session_id: str) -> Login or False:
        matching_user = self.db.query(User).filter(User.name == username, User.password == password, User.enabled == 1).first()
        if matching_user:
            existing_login = self.db.query(Login).filter(Login.user_id == matching_user.id and Login.session_id == session_id).first()
            if not existing_login:
                session_id = uuid4()
                new_login = Login(user_id=matching_user.id, session_id=str(session_id))
                self.db.add(new_login)
                self.db.commit()
                return new_login
            else:
                return existing_login
        return False

    def logout(self, sessionid: str) -> bool:
        try:
            self.db.query(Login).filter(Login.session_id == sessionid).delete()
            self.db.commit()
            return True
        except:
            return False

    def get_session(self, session_id: str) -> Login:
        session = self.db.query(Login).filter(Login.session_id == session_id).first()
        return session

    def get_user_name(self, user_id: str) -> str:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.name

    async def get_user_id(self, username: str, password: str) -> int:
        user = self.db.query(User).filter(User.name == username, User.password == password).first()
        return user.id

    def get_session_user(self, session_id: str) -> User or False:
        session = self.db.query(Login).filter(Login.session_id == session_id).first()
        if session:
            user = self.db.query(User).filter(User.id == session.user_id).first()
            return user
        return False

    def is_owner(self, user_id: int, api_id: int) -> bool:
        owner = self.db.query(Owner).filter(Owner.user_id == user_id, Owner.api_id == api_id).first()
        return owner is not None

    def is_editor(self, user_id: int, api_id: int) -> bool:
        editor = self.db.query(Editor).filter(Editor.user_id == user_id, Editor.api_id == api_id).first()
        return editor is not None

    def change_editor(self, user_id: int, api_id: int) -> bool:
        try:
            old_editor = self.db.query(Editor).filter(Editor.api_id == api_id).first()
            if old_editor:
                self.db.delete(old_editor)
            editor = Editor(user_id=user_id, api_id=api_id)
            self.db.add(editor)
            self.db.commit()
            return True
        except:
            return False

    async def create_api(self, name: str, data: str, channel: str, uid: int, editor: int) -> int or False:
        try:
            if editor == 0:
                return False
            api = Api(name=name, data=data, channel=channel)
            self.db.add(api)
            self.db.commit()
            owner = Owner(user_id=uid, api_id=api.id)
            self.db.add(owner)
            self.db.commit()
            self.change_editor(editor, api.id)
            return api.id
        except:
            return False

    async def delete_api(self, id: int) -> bool:
        try:
            api = self.db.query(Api).filter(Api.id == id).first()
            self.db.delete(api)
            owner = self.db.query(Owner).filter(Owner.api_id == id).first()
            self.db.delete(owner)
            editor = self.db.query(Editor).filter(Editor.api_id == id).first()
            self.db.delete(editor)
            self.db.commit()
            return True
        except:
            return False

    def edit_api(self, id: int, name: str, data: str, channel: str, editor: str) -> bool:
        try:
            api = self.db.query(Api).filter(Api.id == id).first()
            if name and name != api.name:
                api.name = name
            if data and data != api.data:
                api.data = data
            api.channel = channel
            self.db.commit()
            if editor and editor != id:
                self.change_editor(editor, id)
            return True
        except:
            return False

    def edit_user(self, id: int, name: str, password: str, admin: bool, enabled: bool) -> bool:
        try:
            user = self.db.query(User).filter(User.id == id).first()
            if name:
                user.name = name
            if password:
                user.password = password
            user.admin = admin
            user.enabled = enabled
            self.db.commit()
            return True
        except:
            return False

    async def create_user(self, name: str, password: str) -> bool:
        try:
            user = User(name=name, password=password)
            self.db.add(user)
            self.db.commit()
            # self.db.refresh(user)
            return True
        except:
            return False

    async def delete_user(self, id: int) -> bool:
        try:
            user = self.db.query(User).filter(User.id == id).first()
            self.db.delete(user)
            self.db.commit()
            return True
        except:
            return False

    def fetch_api_data(self, id: int, channel: str) -> str or False:
        try:
            api = self.db.query(Api).filter(Api.id == id, Api.channel == channel).first()
            return api.data
        except:
            return False

    def fetch_api_by_name(self, name: str) -> Api or False:
        try:
            api = self.db.query(Api).filter(Api.name == name).first()
            return api
        except:
            return False

    def fetch_user_list(self) -> list[User]:
        users = self.db.query(User).all()
        return users

    def fetch_api_list(self, id: int) -> list[Api]:
        apis = self.db.query(Owner).filter(Owner.user_id == id).all()
        return apis

    def fetch_shared_api_list(self, id: int) -> list[Api]:
        apis = self.db.query(Editor).filter(Editor.user_id == id).all()
        return apis

    def fetch_login_list(self) -> list[Login]:
        logins = self.db.query(Login).all()
        return logins

    def fetch_login(self, session_id: str) -> Login:
        login = self.db.query(Login).filter(Login.session_id == session_id).first()
        return login

    def fetch_api(self, id: int) -> Api:
        api = self.db.query(Api).filter(Api.id == id).first()
        return api

    def fetch_user(self, id: int) -> User:
        user = self.db.query(User).filter(User.id == id).first()
        return user

    def fetch_editor(self, api_id: int) -> Editor:
        editor = self.db.query(Editor).filter(Editor.api_id == api_id).first()
        return editor