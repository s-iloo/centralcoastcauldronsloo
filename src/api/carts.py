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
    print("customer:")
    print(new_cart.customer)
    global cartID
    cartID += 1
    cart_memory[cartID] = []
    #insert row for new cart
    value = {'name':new_cart.customer}
    with db.engine.begin() as connection: 
        # sql = sqlalchemy.text("INSERT INTO carts (customer) VALUES (:value) RETURNING id")
        result = connection.execute(sqlalchemy.text("INSERT INTO carts (customer) VALUES (:name) RETURNING id"), [{"name":new_cart.customer}])
        # result = connection.execute(sql, value)
    print("cartID")
    result = result.fetchone()
    print(result[0])
    return {"cart_id": result[0]}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """  
    # with db.engine.begin() as connection: 
    #     result = connection.execute(sqlalchemy.text("SELECT "))

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
        potionID = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE sku=:itemsku"), {'itemsku':item_sku})
        potionID = potionID.fetchone()
        # potionID = potionID.id
        print("potionID ->  " + str(potionID.id))
        print("qty:")
        print(cart_item.quantity)
        if cart_item.quantity <= potionID.quantity:
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (potion_id, cart_id, quantity) VALUES (:potID, :cartID, :qty)"), {'potID':potionID.id, 'cartID':cart_id, 'qty':cart_item.quantity})
            return "OK"
        else: 
            return "QUANTITY TOO HIGH"

        # if item_sku == "RED_POTION":
        #     if num_red_potions >= cart_item.quantity:
        #         # cart_memory[cartID] = ([{"potion_type": [100, 0, 0, 0], "quantity": cart_item.quantity}])
        #         cart_memory[cart_id].append({"potion_type": [100, 0, 0, 0], "quantity": cart_item.quantity})
        #         return "OK"
        #     else:
        #         return "QUANTITY TOO HIGH"
        # elif item_sku == "GREEN_POTION":
        #     if num_green_potions >= cart_item.quantity:
        #         # cart_memory[cartID] = {"potion_type": [0, 100, 0, 0], "quantity": cart_item.quantity}
        #         cart_memory[cart_id].append({"potion_type": [0, 100, 0, 0], "quantity": cart_item.quantity})
        #     else:
        #         return "QUANTITY TOO HIGH"
        # elif item_sku == "BLUE_POTION":
        #     if num_blue_potions >= cart_item.quantity:
        #         # cart_memory[cartID] = {"potion_type": [0, 0, 100, 0], "quantity": cart_item.quantity}
        #         cart_memory[cart_id].append({"potion_type": [0, 0, 100, 0], "quantity": cart_item.quantity})
        #     else:
        #         return "QUANTITY TOO HIGH"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("payment: ")
    print(cart_checkout.payment)

    with db.engine.begin() as connection: 
        # result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory WHERE id=1"))
        # data = result.fetchone()
        # num_red_potions = data[0]
        # num_green_potions = data[1]
        # num_blue_potions = data[2]
        # gold = data[3]
        # cart = cart_memory[cart_id]
        # print(cart)
        # potion_type = cart["potion_type"]
        total_potions = 0
        #red
        cartItems = connection.execute(sqlalchemy.text("SELECT * FROM cart_items WHERE cart_id=:cartID"), {'cartID':cart_id})
        cartItems = cartItems.fetchall()

        for item in cartItems:
            # potion_type = item_list["potion_type"]
            # qty = item_list["quantity"]
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

            # if potion_type[0] == 100:
            #     num_red_potions -= qty
            #     total_potions +=qty
            #     gold += 50 * qty
            #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_red_potions=:red_potion"), {'goldset':gold, 'red_potion': num_red_potions})
            # if potion_type[1] == 100: 
            #     num_green_potions -= qty
            #     total_potions +=qty
            #     gold += 50 * qty
            #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_green_potions=:green_potion"), {'goldset':gold, 'green_potion': num_green_potions})
            # if potion_type[2] == 100: 
            #     num_blue_potions -= qty
            #     total_potions +=qty
            #     gold += 50 * qty
            #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_blue_potions=:blue_potion"), {'goldset':gold, 'blue_potion': num_blue_potions})
        #if there's stock

        # print("total gold is: " + str(gold))
        print("total gold paid is: "  + str(total_potions * 50))

        # if(num_red_potions > 0):
        #     #check if customer paid enough
        #     #add to gold and subtract from potion stock 
        #     new_num_red_potions = num_red_potions - 1
        #     new_gold = gold + 50
        #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=:goldset, num_red_potions=:potionset"),{'goldset':new_gold,'potionset':new_num_red_potions})
            
        return {"total_potions_bought": total_potions, "total_gold_paid": total_potions*50}
        # else: 
        #     return "OUT OF STOCK"