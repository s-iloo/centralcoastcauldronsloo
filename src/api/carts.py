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


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """    
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 0,
            }
        ]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory WHERE id=1"))
        data = result.fetchone()

        if(data[0] >= cart_item.quantity and item_sku == "RED POTION"):
            return "OK"
        else:
            return "QUANTITY TOO HIGH"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #only allowing customers to buy one potion right now
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_potions = data[0]
        gold = data[1]
        #if there's stock
        if(num_red_potions > 0):
            #check if customer paid enough
            if(int(cart_checkout.payment) >= 50):
                #add to gold and subtract from potion stock 
                new_num_red_potions = num_red_potions - 1
                new_gold = gold + int(cart_checkout.payment)
                
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_red_potions=:potionset"),{'goldset':new_gold}, {'potionset':new_num_red_potions})
                return {"total_potions_bought": 1, "total_gold_paid": 50}
            else: 
                return "INSUFFICIENT PAYMENT"
        else: 
            return "OUT OF STOCK"