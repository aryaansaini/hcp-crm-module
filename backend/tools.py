from langchain_core.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime
import models

def make_tools(db: Session):

    @tool
    def log_interaction(hcp_name: str, topics_discussed: str, sentiment: str = "Neutral",
                         outcomes: str = "", followup_actions: str = "") -> str:
        """
        Naya HCP interaction database mein log karta hai.
        Pehle HCP ko naam se dhoondta hai, agar exist nahi karta to naya bana deta hai.
        sentiment: 'Positive', 'Neutral', ya 'Negative' hona chahiye.
        """
        hcp = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{hcp_name}%")).first()
        if not hcp:
            hcp = models.HCP(name=hcp_name)
            db.add(hcp)
            db.commit()
            db.refresh(hcp)

        interaction = models.Interaction(
            hcp_id=hcp.id,
            interaction_date=datetime.now().date(),
            interaction_time=datetime.now().time(),
            topics_discussed=topics_discussed,
            sentiment=sentiment,
            outcomes=outcomes,
            followup_actions=followup_actions,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return f"Interaction logged successfully for {hcp.name} (Interaction ID: {interaction.id}, Sentiment: {sentiment})"

    @tool
    def edit_interaction(interaction_id: int, field: str, new_value: str) -> str:
        """
        Existing interaction ka koi field update karta hai.
        field: 'topics_discussed', 'sentiment', 'outcomes', ya 'followup_actions' mein se koi ek.
        """
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return f"Error: Interaction ID {interaction_id} not found."

        if hasattr(interaction, field):
            setattr(interaction, field, new_value)
            db.commit()
            return f"Interaction {interaction_id} updated: {field} = {new_value}"
        return f"Error: Field '{field}' does not exist."

    @tool
    def search_hcp_history(hcp_name: str) -> str:
        """
        Kisi HCP ke saath past sab interactions ki history laata hai.
        """
        hcp = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{hcp_name}%")).first()
        if not hcp:
            return f"No HCP found with name '{hcp_name}'."

        interactions = db.query(models.Interaction).filter(models.Interaction.hcp_id == hcp.id).all()
        if not interactions:
            return f"No interactions found for {hcp.name} yet."

        summary = f"History for {hcp.name} ({len(interactions)} interactions):\n"
        for i in interactions:
            summary += f"- [{i.interaction_date}] {i.topics_discussed} (Sentiment: {i.sentiment})\n"
        return summary

    @tool
    def suggest_followup(hcp_name: str, last_topic: str, sentiment: str) -> str:
        """
        Sentiment aur last discussed topic ke basis pe follow-up action suggest karta hai.
        """
        if sentiment.lower() == "positive":
            return f"Suggested follow-up: Schedule next meeting with {hcp_name} within 2 weeks to build on positive momentum around '{last_topic}'. Send additional material."
        elif sentiment.lower() == "negative":
            return f"Suggested follow-up: Address concerns raised about '{last_topic}' with {hcp_name}. Consider involving a medical science liaison for detailed discussion."
        else:
            return f"Suggested follow-up: Send informational follow-up material about '{last_topic}' to {hcp_name} and check in after 3 weeks."

    @tool
    def get_sentiment_summary(hcp_name: str) -> str:
        """
        Kisi HCP ke saath overall sentiment trend batata hai (kitne positive/neutral/negative interactions hue).
        """
        hcp = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{hcp_name}%")).first()
        if not hcp:
            return f"No HCP found with name '{hcp_name}'."

        interactions = db.query(models.Interaction).filter(models.Interaction.hcp_id == hcp.id).all()
        if not interactions:
            return f"No interaction data available for {hcp.name}."

        positive = sum(1 for i in interactions if i.sentiment == "Positive")
        neutral = sum(1 for i in interactions if i.sentiment == "Neutral")
        negative = sum(1 for i in interactions if i.sentiment == "Negative")

        return f"Sentiment summary for {hcp.name}: {positive} Positive, {neutral} Neutral, {negative} Negative (out of {len(interactions)} total interactions)."

    return [log_interaction, edit_interaction, search_hcp_history, suggest_followup, get_sentiment_summary]