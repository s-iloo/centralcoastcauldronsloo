# import sqlalchemy
# from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    # with db.engine.begin() as connection: 
    #      #gives num potions
    #     result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory WHERE id=1"))
    #     if result < 10:
    #     print(result)    
        


    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]
# with db.engine.begin() as connection:
#         result = connection.execute(sql_to_execute)