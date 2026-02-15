import uuid
import hashlib
class Expense:
    def __init__(self,id, date, category, amount, payment_method, rebate=0.0):
        self.id = id 
        self.date = date
        self.category = category
        self.amount = float(amount)
        self.payment_method = payment_method
        self.rebate = float(rebate)
        
        self.hash_value = self.generate_hash()
        
    def __str__(self):
        return (
            f"--{self.id} | {self.date} | {self.category} | "
            f"{self.amount} | {self.payment_method} | {self.rebate}--"
        )

            
    def generate_hash(self):
        hash_input = f"{self.date}|{self.category}|{self.amount}|{self.payment_method}|{self.rebate}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def to_dict(self):
        return{
            
            "id":self.id,
            "date":self.date,
            "category":self.category,
            "amount":self.amount,
            "payment_method":self.payment_method,
            "rebate":self.rebate,
            "hash_value":self.hash_value
        }
        
    # def to_String(self):
    #     print(
    #         f"{self.id}|{self.date}|{self.category}|{self.amount}|{self.payment_method}|{self.rebate}"
    #     )
        
    @classmethod
    def from_dict(cls, data):
        obj = cls(
            id=data["id"],
            date=data["date"],
            category=data["category"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            rebate=data.get("rebate", 0.0)
        )

        obj.hash_value = data.get("hash_value", obj.generate_hash())
        return obj
