import streamlit as st
from typing import List, Dict
import uuid

def add_custom_css():
    """Add custom CSS for horizontal source boxes."""
    st.markdown("""
        <style>
        .sources-container {
            display: flex;
            flex-direction: row;
            gap: 10px;
            overflow-x: auto;
            padding: 10px 0;
        }
        .source-box {
            min-width: 200px;
            max-width: 300px;
            padding: 10px 15px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .source-box:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .source-title {
            font-weight: 600;
            color: #1e88e5;
            margin-bottom: 5px;
        }
        .source-preview {
            font-size: 0.9em;
            color: #666;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        </style>
    """, unsafe_allow_html=True)

def format_source_preview(text: str, max_length: int = 100) -> str:
    """Format source text preview."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def show_source_page(source: Dict):
    """Display source content in detail."""
    st.title("Source Details")
    
    st.markdown(f"### {source['metadata']['source']}")
    st.markdown(f"**Page:** {source['metadata']['page_num']}")
    
    if source['metadata'].get('content_type') == 'table':
        st.markdown("#### Table Information")
        st.markdown(f"- Table Number: {source['metadata'].get('table_num')}")
        st.markdown(f"- Rows: {source['metadata'].get('row_count')}")
        st.markdown(f"- Columns: {source['metadata'].get('col_count')}")
    
    st.markdown("### Content")
    st.markdown(source['text'])
    
    st.markdown("### Metadata")
    st.json(source['metadata'])

def render_sources(sources: List[Dict], message_idx: int):
    """Render sources in horizontal boxes with click handling."""
    st.markdown('<div class="sources-container">', unsafe_allow_html=True)
    
    cols = st.columns(min(len(sources), 4))  # Show up to 4 sources in a row
    
    for idx, (source, col) in enumerate(zip(sources, cols)):
        with col:
            # Create unique key for each source button using message_idx and source idx
            source_key = f"source_{message_idx}_{idx}_{source['metadata']['chunk_id']}"
            
            # Create clickable container
            if st.button(
                f"📄 {source['metadata']['source']} (Page {source['metadata']['page_num']})",
                key=source_key,
                use_container_width=True,
            ):
                st.session_state.selected_source = source
                st.session_state.show_source_page = True
            
            # Show preview
            st.markdown(
                f"<div class='source-preview'>{format_source_preview(source['text'])}</div>",
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_interface(
    chat_history: List[Dict[str, str]],
    sources: List[Dict] = None
):
    """Render the chat interface with horizontal source boxes."""
    # Initialize session state for source viewing
    if 'show_source_page' not in st.session_state:
        st.session_state.show_source_page = False
    if 'selected_source' not in st.session_state:
        st.session_state.selected_source = None
    
    # Show source page if selected
    if st.session_state.show_source_page and st.session_state.selected_source:
        show_source_page(st.session_state.selected_source)
        if st.button("← Back to Chat", key="back_to_chat"):
            st.session_state.show_source_page = False
            st.session_state.selected_source = None
            st.rerun()
        return None
    
    # Regular chat interface
    st.header("Chat")
    
    for idx, message in enumerate(chat_history):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and sources and idx == len(chat_history) - 1:
                render_sources(sources, idx)
    
    return st.chat_input("Ask a question about your documents...")