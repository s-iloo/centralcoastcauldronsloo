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
    print("customer:")
    print(new_cart.customer)
    #insert row for new cart
    value = {'name':new_cart.customer}
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("INSERT INTO carts (customer) VALUES (:name) RETURNING id"), [{'name':new_cart.customer}])
    print("cartID")
    result = result.fetchone()
    print(result[0])
    return {"cart_id": result[0]}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """  
    # with db.engine.begin() as connection: 
    #     result = connection.execute(sqlalchemy.text("SELECT "))
    # with db.engine.begin() as connection: 
    #     result = connection.execute(sqlalchemy.text("SELECT * FROM cart_items WHERE cart_id=:id"), {"id": cart_id})
        
    return 
    # return cart_memory.get(cart_id)
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
        potionID = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE sku=:itemsku"), {'itemsku':item_sku})
        potionID = potionID.fetchone()
        print("potionID ->  " + str(potionID.id))
        print("qty:")
        print(cart_item.quantity)
        if cart_item.quantity < potionID.quantity:
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (potion_id, cart_id, quantity) VALUES (:potID, :cartID, :qty)"), {'potID':potionID.id, 'cartID':cart_id, 'qty':cart_item.quantity})
            return "OK"
        else: 
            return "QUANTITY TOO HIGH"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("payment: ")
    print(cart_checkout.payment)

    with db.engine.begin() as connection: 
        total_potions = 0
        cartItems = connection.execute(sqlalchemy.text("SELECT * FROM cart_items WHERE cart_id=:cartID"), {'cartID':cart_id})
        cartItems = cartItems.fetchall()

        for item in cartItems:
            potionID = item.potion_id
            qty = item.quantity
            print("potion ID")
            print(potionID)
            print("qty")
            print(qty)
            potionType = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE id=:potion_id"), {'potion_id': potionID})
            potionType = potionType.fetchone()
            print("potion sku")
            print(potionType.sku)
            
            #if purple decrement purple qty in potions
            print("you're buying " + potionType.sku)
            connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity - :qtybought WHERE sku = :potsku"), {'qtybought':qty, 'potsku':potionType.sku})                
            #increment total_potions
            total_potions += qty
            #increment gold
            connection.execute(sqlalchemy.text("UPDATE global_inventory set gold= gold + :price"), {'price':qty * 50})
        print("total gold paid is: "  + str(total_potions * 50))
         
        return {"total_potions_bought": total_potions, "total_gold_paid": total_potions*50}