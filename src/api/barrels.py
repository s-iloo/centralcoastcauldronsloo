import sqlalchemy
from src import database as db
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
    with db.engine.begin() as connection: 
        print("barrels_delivered")
        print(barrels_delivered)
        result = connection.execute(sqlalchemy.text("SELECT gold, num_red_ml, num_blue_ml, num_green_ml FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        gold = data[0]
        num_red_ml = data[1]
        num_blue_ml = data[2]
        num_green_ml = data[3]

        for barrel in barrels_delivered:
            #means its red
            if barrel.sku == "SMALL_RED_BARREL":
                #only buying one barrel rn 
                num_red_ml += barrel.ml_per_barrel * barrel.quantity
                gold -= barrel.price
            #means its green 
            elif barrel.sku == "SMALL_GREEN_BARREL": 
                num_green_ml += barrel.ml_per_barrel * barrel.quantity
                gold -= barrel.price
            elif barrel.sku == "SMALL_BLUE_BARREL":
                num_blue_ml += barrel.ml_per_barrel * barrel.quantity
                gold -= barrel.price
            
            
        # remaining_gold = gold - price
        # remaining_ml = num_red_ml + ml
        value ={'goldset':gold}
        sql = sqlalchemy.text("UPDATE global_inventory SET gold=:goldset")
        connection.execute(sql, value)

        value2 = {'red_ml':num_red_ml}
        sql2 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:red_ml")
        connection.execute(sql2, value2)

        value3 = {'green_ml': num_green_ml}
        sql3 = sqlalchemy.text("UPDATE global_inventory SET num_green_ml=:green_ml")
        connection.execute(sql3, value3)

        value4 = {'blue_ml': num_blue_ml}
        sql4 = sqlalchemy.text("UPDATE global_inventory SET num_blue_ml=:blue_ml")
        connection.execute(sql4, value4)

        print("your remaining gold is " + str(gold))
        print("your remaining red ml is " + str(num_red_ml) + ", green ml is " + str(num_green_ml) + ", blue ml is " + str(num_blue_ml))

        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    with db.engine.begin() as connection: 
        print(wholesale_catalog)
        #get num red potions
        # result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory WHERE id=1"))
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions, gold FROM global_inventory WHERE id=1"))
        #parse to get int
        data = result.fetchone()
        # num_red_potions = data[0]

        # getting all the inventory that i have and my gold
        num_red_potions = data[0]
        num_blue_potions = data[1]
        num_green_potions = data[2]
        gold = data[3]

        potions = [("red", num_red_potions), ("blue", num_blue_potions), ("green", num_green_potions)]
        potions = sorted(potions, key=lambda x: x[1])
    
        print(gold)
        print(potions)
        plan = []
        for potion in potions:
            pot_type = potion[0]
            for barrel in wholesale_catalog:
                if pot_type == "red":
                    if barrel.sku == "SMALL_RED_BARREL":
                        if gold >= barrel.price:
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_RED_BARREL", "quantity": 1}) 
                if pot_type == "blue":
                    if barrel.sku == "SMALL_BLUE_BARREL":
                        if gold >= barrel.price: 
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_BLUE_BARREL", "quantity": 1})
                if pot_type == "green":
                    if barrel.sku == "SMALL_GREEN_BARREL":
                        if gold >= barrel.price: 
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_GREEN_BARREL", "quantity": 1})
        print(plan)
        print(gold)

        return plan