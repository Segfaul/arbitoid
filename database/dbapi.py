import inspect
from datetime import datetime, date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import User


class DatabaseConnector:

    def __init__(self, params: dict, logger=None):
        connection_string = f"postgresql://{params['username']}:{params['password']}" \
                            f"@{params['ip']}:{params['port']}/{params['database']}"
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(self.engine)
        self.logger = logger
        self.create_tables()

    def create_tables(self) -> int:
        func_name = inspect.currentframe().f_code.co_name

        try:

            User.metadata.create_all(self.engine)

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0
            return 0

    '''             
    ----------------------------------------------
                    Client logic             
    ----------------------------------------------
    '''

    def get_user(self, tg_id: int) -> list or int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            data = session.query(User).filter(User.id == tg_id).first().as_dict()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return data

    def check_sub(self, tg_id: int) -> str or int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            if user.is_admin:
                return "XX-XX-XX"

            if user.sub:

                if user.sub >= datetime.now().date():
                    return user.sub
                else:
                    return 1

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return 1

    def input_user(self, tg_id: int, username: str = None) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = User(id=tg_id, username=username)

            if not session.get(User, tg_id):
                session.add(user)
                session.commit()
                return 0

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return 1

    def switch_status(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()
        res = 0

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            if user.status == 0:
                user.status = True
                res += 1
            else:
                user.status = False

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return res

    def resize_percent(self, tg_id: int, percent: int or float) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            user.percent = percent

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}/{percent}") if self.logger else 0

        return 0

    def add_req(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            user.req_num += 1

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return 0

    def remove_req(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            user.req_num = 0

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

        return 0

    def reset_req(self) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            users = session.query(User).all()

            for user in users:
                user.req_num = 0

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}") if self.logger else 0

        return 0

    '''             
   ----------------------------------------------
                   Admin logic             
   ----------------------------------------------
    '''

    @property
    def get_stats(self) -> dict or int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()
        stats: dict = {}

        try:
            stats['all'] = [user.as_dict() for user in session.query(User).all()]
            stats['with_sub'] = [
                user.as_dict() for user in session.query(User).filter(
                    (User.sub.is_not(None)) & (User.sub >= datetime.now())
                ).all()
            ]

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}") if self.logger else 0

        return stats

    @property
    def get_admins(self) -> list or int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            data = [user.as_dict() for user in session.query(User).filter(User.is_admin.is_(True)).all()]

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}") if self.logger else 0

        return data

    @property
    def get_ready_users(self) -> list or int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            data = [
                user.as_dict() for user in session.query(User).filter(
                    (User.is_admin.is_(True)) | (
                        (User.status.is_(True)) &
                        (User.sub.is_not(None)) &
                        (User.sub > datetime.now())
                    )
                ).all()
            ]

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}") if self.logger else 0

        return data

    def add_sub(self, tg_id: int, np: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            new_sub = date.today() + timedelta(60)
            user = session.query(User).filter(User.id == tg_id).first()

            if np == 0:
                user.sub = None
            elif np == 1:
                user.sub = new_sub

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}/{np}") if self.logger else 0

        return 0

    def add_admin(self, tg_id: int, np: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        session = self.Session()

        try:
            user = session.query(User).filter(User.id == tg_id).first()

            if np == 0:
                user.is_admin = False
            elif np == 1:
                user.is_admin = True

            session.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            session.close()
            self.logger.info(f"{func_name}/{tg_id}/{np}") if self.logger else 0

        return 0
