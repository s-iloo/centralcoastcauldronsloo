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
        # result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory WHERE id=1"))
        #get all the qty of potions we have
        # red = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=1"))
        # green = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=2"))
        # blue = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=4"))
        # purple = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=3"))
        # red = red.fetchone()
        # red = red[0]
        # green = green.fetchone()
        # green = green[0]
        # purple = purple.fetchone()
        # purple = purple[0]
        # blue = blue.fetchone()
        # blue = blue[0]

        # data = result.fetchone()
        # # num_red_potions = data[0]
        # num_red_ml = data[0]
        # # num_green_potions = data[2]
        # num_green_ml = data[1]
        # # num_blue_potions = data[4]
        # num_blue_ml = data[2]
        rows = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        rows = rows.fetchall()

        for row in rows: 
            for potion in potions_delivered:
                if [row.red, row.green, row.blue, row.dark] == potion.potion_type:
                    print(row.sku)
                    print(potion.quantity)
                    connection.execute(sqlalchemy.text("UPDATE potions SET quantity=quantity + :qty WHERE sku=:rowsku"), {'qty':potion.quantity, 'rowsku':row.sku})
                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml= num_red_ml - :rowred, num_green_ml = num_green_ml - :rowgreen, num_blue_ml = num_blue_ml - :rowblue"), {'rowred':row.red * potion.quantity, 'rowgreen':row.green * potion.quantity, 'rowblue':row.blue * potion.quantity})
                    #UPDATE THE ROW THROUGH THE SKU WITH QTY
                    #UPDATE THE GLOBAL INVENTORY 

            #if we have a red potion add to num_red_potions
            #also subtract from num red ml when bottling potions 



            # if potion.potion_type[0] == 0 and potion.potion_type[1] == 50 and potion.potion_type[2] == 50:
            #     #seahawks
            #     seahawks += potion.quantity
            #     num_green_ml -= potion.quantity * 50
            #     num_blue_ml -= potion.quantity * 50
            # if potion.potion_type[0] == 50 and potion.potion_type[1] == 50 and potion.potion_type[2] == 0: 
            #     #christmas
            #     christmas += potion.quantity
            #     num_green_ml -= potion.quantity * 50
            #     num_red_ml -= potion.quantity * 50
            # if potion.potion_type[0] == 50 and potion.potion_type[1] == 0 and potion.potion_type[2] == 50:
            #     #purple
            #     purple += potion.quantity
            #     num_red_ml -= potion.quantity * 50
            #     num_blue_ml -= potion.quantity * 50



            # if potion.potion_type[0] == 100:
            #     num_red_potions += potion.quantity
            #     num_red_ml -= potion.quantity * 100
            # elif potion.potion_type[1] == 100:
            #     num_green_potions += potion.quantity
            #     num_green_ml -= potion.quantity * 100
            # elif potion.potion_type[2] == 100: 
            #     num_blue_potions += potion.quantity
            #     num_blue_ml -= potion.quantity * 100
        
        # value = {'red_potions':num_red_potions}
        # value2 = {'red_ml':num_red_ml}
        # value3 = {'green_potions': num_green_potions}
        # value4 = {'green_ml':num_green_ml}
        # value5 = {'blue_potions': num_blue_potions}
        # value6 = {'blue_ml': num_blue_ml}

        # value = {'seahawks_amt':seahawks}
        # value2 = {'christmas_amt':christmas}
        # value3 = {'purple_amt':purple}
        # value4 = {'red_ml':num_red_ml}
        # value5 = {'green_ml':num_green_ml}
        # value6 = {'blue_ml': num_blue_ml}

        # sql = sqlalchemy.text("UPDATE potions SET quantity=:seahawks_amt WHERE id=1")
        # sql2 = sqlalchemy.text("UPDATE potions SET quantity=:christmas_amt WHERE id=2")
        # sql3 = sqlalchemy.text("UPDATE potions SET quantity=:purple_amt WHERE id=3")
        # sql4 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:red_ml")
        # sql5 = sqlalchemy.text("UPDATE global_inventory SET num_green_ml=:green_ml")
        # sql6 = sqlalchemy.text("UPDATE global_inventory SET num_blue_ml=:blue_ml")
        # connection.execute(sql, value)
        # connection.execute(sql2, value2)
        # connection.execute(sql3, value3)
        # connection.execute(sql4, value4)
        # connection.execute(sql5, value5)
        # connection.execute(sql6, value6)
        # sql = sqlalchemy.text("UPDATE global_inventory SET num_red_potions=:red_potions",)
        # sql2 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:red_ml")
        # connection.execute(sql, value)
        # connection.execute(sql2, value2)

        # sql3 = sqlalchemy.text("UPDATE global_inventory SET num_green_potions=:green_potions",)
        # sql4 = sqlalchemy.text("UPDATE global_inventory SET num_green_ml=:green_ml") 
        # connection.execute(sql3, value3)
        # connection.execute(sql4, value4)

        # sql5 = sqlalchemy.text("UPDATE global_inventory SET num_blue_potions=:blue_potions",)
        # sql6 = sqlalchemy.text("UPDATE global_inventory SET num_blue_ml=:blue_ml") 
        # connection.execute(sql5, value5)
        # connection.execute(sql6, value6)


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

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory WHERE id=1"))
        red = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=1"))
        green = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=2"))
        purple = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=3"))
        blue = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=4"))
        data = result.fetchone()
        num_red_ml = data[0]
        num_green_ml = data[1]
        num_blue_ml = data[2]
        red = red.fetchone()
        red = red[0]
        green = green.fetchone()
        green = green[0]
        purple = purple.fetchone()
        purple = purple[0]
        blue = blue.fetchone()
        blue = blue[0]

        potions = [("PURPLE", purple), ("RED", red), ("GREEN", green), ("BLUE", blue)]
        potions = sorted(potions, key=lambda x: x[1])
        print("new potions sorted")
        print(potions)

        red_qty = (num_red_ml // 100) // 2
        green_qty = (num_green_ml // 100) // 2
        blue_qty = (num_blue_ml // 100) // 2 
        purple_qty = min(num_red_ml // 100, num_blue_ml // 100)

        total = red_qty + green_qty + blue_qty + purple_qty

        print("red quantity: " + str(red_qty))
        print("green quantity: " + str(green_qty))
        print("blue quantity: " + str(blue_qty))
        print("purple quantity: " + str(purple_qty))
        result = []
        potionsQty = dict([("PURPLE", purple_qty), ("RED", red_qty), ("GREEN", green_qty), ("BLUE", blue_qty)])


        #i should probably add a num_sold col to try and make sure I sell equal amt
        #loop through in order of potions i need to make

        #means we have qty to bottle
        if total > 0: 
            potions = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
            potions = potions.fetchall()
            for pot in potions: 
                if potionsQty[pot.sku] > 0: 
                    result.append({
                        "potion_type": [pot.red, pot.green, pot.blue, pot.dark],
                        "quantity": potionsQty[pot.sku],
                    })

        # for potion in potions: 
        #     pot_type = potion[0]
        #     if pot_type == "red":
        #         if red_qty > 0:
        #             result.append({
        #                         "potion_type": [100, 0, 0, 0],
        #                         "quantity": red_qty,
        #                     })
        #     if pot_type == "green":
        #         if green_qty > 0: 
        #             result.append({
        #                         "potion_type": [0, 100, 0, 0],
        #                         "quantity": green_qty,
        #                     })
        #     if pot_type == "blue":
        #         if blue_qty > 0: 
        #             result.append({
        #                         "potion_type": [0, 0, 100, 0],
        #                         "quantity": blue_qty,
        #                     })
        #     if pot_type == "purple":
        #         if purple_qty > 0:
        #             result.append({
        #                         "potion_type": [50, 0, 50, 0],
        #                         "quantity": purple_qty,
        #                     })
                    
        return result
