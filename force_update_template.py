from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models
from ferreteria_refactor.backend_api import template_presets

def update_template():
    db = SessionLocal()
    try:
        # Fetch the current config
        config = db.query(models.BusinessConfig).filter(models.BusinessConfig.key == "ticket_template").first()
        
        # Get the new clean 'Modern' template (since that matches the user's current layout)
        new_template = template_presets.get_modern_template()
        
        if config:
            print("Found existing template config. Updating...")
            config.value = new_template
        else:
            print("No template config found. Creating new...")
            config = models.BusinessConfig(key="ticket_template", value=new_template)
            db.add(config)
            
            db.commit()
            print(">> Ticket template successfully updated in database!")
            print("New content preview:")
            print(new_template[:200] + "...")
            
    except Exception as e:
        print(f"!! Error updating template: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_template()
