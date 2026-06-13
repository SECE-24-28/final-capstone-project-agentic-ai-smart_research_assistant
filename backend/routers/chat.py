from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import SessionLocal
from ..models import ChatSession, ChatMessage
from ..schemas import ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/session", response_model=ChatSessionResponse)
def create_session(session_data: ChatSessionCreate, db: Session = Depends(get_db)):
    """Creates a new chat session."""
    db_session = ChatSession(title=session_data.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    # Convert datetime to string for response
    return ChatSessionResponse(
        id=db_session.id,
        title=db_session.title,
        created_at=db_session.created_at.isoformat(),
        updated_at=db_session.updated_at.isoformat(),
        messages=[]
    )


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    """Retrieves all chat sessions, ordered by most recently updated."""
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    results = []
    for s in sessions:
        results.append(ChatSessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
            messages=[] # Don't fetch all messages for the list view
        ))
    return results


@router.get("/session/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific chat session with all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = []
    for m in session.messages:
        messages.append(ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            agent_type=m.agent_type,
            created_at=m.created_at.isoformat()
        ))
        
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=messages
    )


@router.delete("/session/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Deletes a chat session and cascades to delete all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    db.delete(session)
    db.commit()
    return {"status": "success"}


@router.post("/message", response_model=ChatMessageResponse)
def create_message(message_data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Creates a new message within an existing session and updates the session's updated_at timestamp."""
    session = db.query(ChatSession).filter(ChatSession.id == message_data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # If this is the very first user message and the title is 'New Research', update the title
    if message_data.role == "user" and session.title == "New Research":
        words = message_data.content.split()
        new_title = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
        session.title = new_title
        
    # Update the session's timestamp
    session.updated_at = datetime.utcnow()
    
    db_msg = ChatMessage(
        session_id=message_data.session_id,
        role=message_data.role,
        content=message_data.content,
        agent_type=message_data.agent_type
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    
    return ChatMessageResponse(
        id=db_msg.id,
        session_id=db_msg.session_id,
        role=db_msg.role,
        content=db_msg.content,
        agent_type=db_msg.agent_type,
        created_at=db_msg.created_at.isoformat()
    )
