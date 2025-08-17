from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    api_key: str = Field(
        description="API key for accessing the remote model"
    )
    model_name: str = Field(
        description="name of the model"
    )

    save_history: bool = Field(
        description="save history of interactions with the model"
    )
    
    description: str = Field(
        description="description of the agent what it does"
    )

    main_prompt: str = Field(
        description="main prompt for model"
    )

    agent_id: str = Field(
        description="id for identifying the agent"
    )

    # works as state too
    take_user_input: bool = Field(
        default=True,
        description="if false it will send response to master and generate response if true it will take user input"
    )

    recall_itself: bool = False
