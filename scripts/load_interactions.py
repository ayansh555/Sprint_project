import pandas as pd

from app.database.connection import SessionLocal
from app.database.models import User, UserInteraction


CSV_FILE = "data/user_interactions.csv"


def load_interactions():

    print("Loading user interaction dataset...")

    df = pd.read_csv(CSV_FILE)

    print(
        f"Found {len(df)} interactions."
    )

    db = SessionLocal()

    try:

        # -----------------------------
        # Create users
        # -----------------------------

        user_ids = (
            df["User_ID"]
            .dropna()
            .astype(str)
            .unique()
        )

        users = [
            User(user_id=user_id)
            for user_id in user_ids
        ]

        db.add_all(users)

        # -----------------------------
        # Create interactions
        # -----------------------------

        interactions = []

        for _, row in df.iterrows():

            interaction = UserInteraction(
                interaction_id=str(
                    row["Interaction_ID"]
                ),
                user_id=str(
                    row["User_ID"]
                ),
                product_id=str(
                    row["Product_ID"]
                ),
                interaction_type=row[
                    "Interaction_Type"
                ],
                timestamp=pd.to_datetime(
                    row["Timestamp"]
                )
            )

            interactions.append(
                interaction
            )

        db.add_all(interactions)

        db.commit()

        print(
            f"Successfully inserted "
            f"{len(users)} users."
        )

        print(
            f"Successfully inserted "
            f"{len(interactions)} interactions."
        )

    except Exception as e:

        db.rollback()

        print("ERROR:", e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    load_interactions()