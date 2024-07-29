import os
from utils.logger import logger
import dotenv
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dotenv.load_dotenv()

SQLALCHEMY_DB_URL = os.environ.get("DB_CONNECTION_STRING")

engine = create_engine(
    SQLALCHEMY_DB_URL,
    # echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_db_transactions(directive: str, data: any, model: any):
    session = SessionLocal()
    try:
        if directive == "create":
            session.add(data)
            final_resp = {
                "status": 202,
                "message": "Succesfully created",
            }

        elif directive == "update":
            instance_id = data["id"]
            del data["id"]

            logger.info(f"Updating database object for {model} --- > {instance_id}")
            session.execute(update(model).where(model.id == instance_id).values(**data))
            data = session.query(model).filter(model.id == instance_id).first()

            final_resp = {
                "status": 200,
                "message": "Succesfully updated",
            }

        elif directive == "delete":
            object_to_delete = (
                session.query(model).filter(model.id == data["id"]).first()
            )
            session.delete(object_to_delete)
            final_resp = {
                "status": 204,
                "message": f'Successfully deleted {data['id']}',
            }

        elif directive == "get":
            if data.get("id"):
                final_resp = jsonable_encoder(
                    session.query(model).filter_by(**data).first()
                )
            else:
                limit = data["limit"]
                offset = (data["page"] - 1) * limit
                del data["limit"]
                del data["page"]

                final_resp = jsonable_encoder(
                    session.query(model)
                    .filter_by(**data)
                    .limit(limit)
                    .offset(offset)
                    .all()
                )

        session.commit()

        if directive in ["create", "update"]:
            print(type(data))
            session.refresh(data)
            final_resp["data"] = data.__dict__
            del final_resp["data"]["_sa_instance_state"]

        return final_resp

    except Exception as e:
        session.rollback()

        if e.__str__().__contains__("UndefinedTable"):
            Base.metadata.create_all(bind=engine)

        if e.__str__().__contains__("UndefinedColumn"):
            # Fix this to update columns
            Base.metadata.create_all(bind=engine)

        logger.exception(e)

        return {"status": 500, "error": e.__str__()}

    finally:
        session.close()
