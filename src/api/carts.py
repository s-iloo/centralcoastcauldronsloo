import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

cart_memory = {}

cartID = 0
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    global cartID
    cartID += 1
    cart_memory[cartID] = []
    return {"cart_id": cartID}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """  
    return cart_memory.get(cart_id)
    # return [
            # {
            #     "potion_type": [100, 0, 0, 0],
            #     "quantity": 0,
            # }
    #     ]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_potions = data[0]
        num_green_potions = data[1]
        num_blue_potions = data[2]
        if item_sku == "RED_POTION":
            if num_red_potions >= cart_item.quantity:
                # cart_memory[cartID] = ([{"potion_type": [100, 0, 0, 0], "quantity": cart_item.quantity}])
                cart_memory[cartID].append({"potion_type": [100, 0, 0, 0], "quantity": cart_item.quantity})
                return "OK"
            else:
                return "QUANTITY TOO HIGH"
        elif item_sku == "GREEN_POTION":
            if num_green_potions >= cart_item.quantity:
                # cart_memory[cartID] = {"potion_type": [0, 100, 0, 0], "quantity": cart_item.quantity}
                cart_memory[cartID].append({"potion_type": [0, 100, 0, 0], "quantity": cart_item.quantity})
            else:
                return "QUANTITY TOO HIGH"
        elif item_sku == "BLUE_POTION":
            if num_blue_potions >= cart_item.quantity:
                # cart_memory[cartID] = {"potion_type": [0, 0, 100, 0], "quantity": cart_item.quantity}
                cart_memory[cartID].append({"potion_type": [0, 0, 100, 0], "quantity": cart_item.quantity})
            else:
                return "QUANTITY TOO HIGH"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #only allowing customers to buy one potion right now
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_potions = data[0]
        num_green_potions = data[1]
        num_blue_potions = data[2]
        gold = data[3]
        cart = cart_memory[cart_id]
        print(cart)
        # potion_type = cart["potion_type"]
        total_potions = 0
        #red
        for item_list in cart:
            potion_type = item_list["potion_type"]
            print("potion_type")
            print(potion_type)
            if potion_type[0] == 100:
                num_red_potions -= 1
                total_potions +=1
                gold += 50
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_red_potions=:red_potion"), {'goldset':gold, 'red_potion': num_red_potions})
            if potion_type[1] == 100: 
                num_green_potions -= 1
                total_potions +=1
                gold += 50
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_green_potions=:green_potion"), {'goldset':gold, 'green_potion': num_green_potions})
            if potion_type[2] == 100: 
                num_blue_potions -= 1
                total_potions +=1
                gold += 50
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_blue_potions=:blue_potion"), {'goldset':gold, 'blue_potion': num_blue_potions})
        #if there's stock

        

        # if(num_red_potions > 0):
        #     #check if customer paid enough
        #     #add to gold and subtract from potion stock 
        #     new_num_red_potions = num_red_potions - 1
        #     new_gold = gold + 50
        #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_red_potions=:potionset"),{'goldset':new_gold,'potionset':new_num_red_potions})
            
        return {"total_potions_bought": total_potions, "total_gold_paid": total_potions*50}
        # else: 
        #     return "OUT OF STOCK"