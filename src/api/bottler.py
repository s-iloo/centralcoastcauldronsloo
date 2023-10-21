import random
import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    with db.engine.begin() as connection: 
        print(potions_delivered)
        rows = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        rows = rows.fetchall()

        for row in rows: 
            for potion in potions_delivered:
                if [row.red, row.green, row.blue, row.dark] == potion.potion_type:
                    print(row.sku)
                    print(potion.quantity)
                    print("potion id is " + str(row.id))
                    connection.execute(sqlalchemy.text("INSERT INTO potion_ledger (change, potion_id) VALUES (:qty, :id)"), {'qty':potion.quantity, 'id':row.id})
                    if row.red > 0:
                        connection.execute(sqlalchemy.text("INSERT INTO red_ml_ledger (change) VALUES (:red)"), {'red':-row.red * potion.quantity})
                    if row.green > 0: 
                        connection.execute(sqlalchemy.text("INSERT INTO green_ml_ledger (change) VALUES (:green)"), {'green':-row.green * potion.quantity})
                    if row.blue > 0:
                        connection.execute(sqlalchemy.text("INSERT INTO blue_ml_ledger (change) VALUES (:blue)"), {'blue':-row.blue * potion.quantity})
        print(potions_delivered)
        return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    with db.engine.begin() as connection:
        # result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory WHERE id=1"))
        red = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM red_ml_ledger"))
        green = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM green_ml_ledger"))
        blue = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM blue_ml_ledger"))
        red = red.fetchone()
        green = green.fetchone()
        blue = blue.fetchone()
        num_red_ml = red.balance
        num_blue_ml = blue.balance
        num_green_ml = green.balance

        potion_inventory = connection.execute(sqlalchemy.text("SELECT red, green, blue, quantity, id FROM potions"))
        potion_inventory = potion_inventory.fetchall()

        potion_list = []
        for row in potion_inventory: 
            quantity = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM potion_ledger WHERE potion_id = :id"), {'id': row.id})
            quantity = quantity.fetchone()
            potion_list.append(([row.red, row.green, row.blue, 0], quantity.balance))
        print("potion_list")
        print(potion_list)

        # data = result.fetchone()
        # num_red_ml = data[0]
        # num_green_ml = data[1]
        # num_blue_ml = data[2]
        random.shuffle(potion_list)
        #sort the potion_list by qty
        potion_list = sorted(potion_list, key=lambda x: x[1])
        print("new potions sorted")
        print(potion_list)
        result = []
        qty_list = []
        red_qty = 0
        blue_qty = 0
        green_qty = 0
        for potion in potion_list: 
            pot_type = potion[0]
            qty_list = []
            if pot_type[0] <= num_red_ml and pot_type[1] <= num_green_ml and pot_type[2] <= num_blue_ml: 
                print("at top we have")
                print("red " + str(num_red_ml))
                print("blue " + str(num_blue_ml))
                print("green " + str(num_green_ml))
                if pot_type[0] > 0: 
                    #gives me how much of this pot type i can make
                    red_qty = num_red_ml // pot_type[0]
                    qty_list.append(red_qty)
                    num_red_ml -= red_qty * pot_type[0]
                    print("remaining red ml is " + str(num_red_ml))
                if pot_type[1] > 0: 
                    green_qty = num_green_ml // pot_type[1]
                    qty_list.append(green_qty)
                    num_green_ml -= green_qty * pot_type[1]
                if pot_type[2] > 0: 
                    blue_qty = num_blue_ml // pot_type[2]
                    qty_list.append(blue_qty)
                    num_blue_ml -= blue_qty * pot_type[2]
            if len(qty_list) > 0:
                result.append({
                    "potion_type": [pot_type[0], pot_type[1], pot_type[2], pot_type[3]],
                    "quantity": min(qty_list)
                })
                
        print("calculated qty list")
        print(qty_list)
        print(result)
                    
        return result
