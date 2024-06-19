import os
import dotenv
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dotenv.load_dotenv()

SQLALCHEMY_DB_URL= os.environ.get('DB_CONNECTION_STRING')

engine = create_engine(
    SQLALCHEMY_DB_URL,
    # echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_db_transactions(directive:str, data:any, model:any):
    session = SessionLocal()
    try:
        if directive == 'create':
            session.add(data)
            final_resp = {
                'status':202,
                'message':f'Succesfully created',
                'data': dict(data.__str__())
            }

        elif directive == 'update':
            session.add(data)
            final_resp = {
                'status':200,
                'message':f'Succesfully updated',
                'data': dict(data.__str__())
            }
            
        elif directive == 'delete':
            object_to_delete = session.query(model).filter(model.id == data['id']).first()
            session.delete(object_to_delete)
            final_resp = {
                'status':204,
                'message': f'Successfully deleted {data['id']}'
            }

        elif directive == 'get' and data.get("id"):
            final_resp = jsonable_encoder(session.query(model).filter(model.id == data['id']).all())

        elif directive == 'get':
            # Change this to filter
            final_resp = jsonable_encoder(session.query(model).all())

        session.commit()

        if directive in ['create', 'update'] and data.id:
            final_resp['data']['id'] = data.id
        
        return final_resp
         
    except Exception  as e :
        session.rollback()

        if  e.__str__().__contains__('UndefinedTable'):
            Base.metadata.create_all(bind=engine)

        if e.__str__().__contains__('UndefinedColumn'):
            # Fix this to update columns 
            Base.metadata.create_all(bind=engine)

        print("This is the error =====>>\n", e, "\n======>")
        # raise e
        return e.args
    finally:
        session.close()

