import streamlit as st
import boto3

# --- AWS Configuration ---
KNOWLEDGE_BASE_ID = 'HKGMYP5EAI' 
MODEL_ARN = 'arn:aws:bedrock:us-east-1:<YOUR_AWS_ACCOUNT_ID>:inference-profile/us.anthropic.claude-sonnet-4-6'

def query_bedrock_rag(query):
    """Queries the Amazon Bedrock Knowledge Base and returns the answer and sources."""
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    try:
        response = client.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': MODEL_ARN
                }
            }
        )
        
        answer = response['output']['text']
        
        # Extract unique sources
        sources = set()
        for citation in response.get('citations', []):
            for reference in citation.get('retrievedReferences', []):
                location = reference['location']['s3Location']['uri']
                filename = location.split('/')[-1]
                sources.add(filename)
                
        return answer, list(sources)
    except Exception as e:
        return f"Error calling Bedrock: {str(e)}", []

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Enterprise HR Knowledge Assistant", page_icon="🤖", layout="centered")

# --- Professional Branding Sidebar ---
with st.sidebar:
    st.markdown("### 👨‍💻 System Architect")
    st.markdown("**Syed Taher**")
    st.markdown("Cloud & Generative AI Engineer")
    st.divider()
    st.markdown("### 🏗️ Architecture Stack")
    st.markdown("- **Cloud Provider:** AWS")
    st.markdown("- **LLM:** Claude Sonnet 4.6")
    st.markdown("- **Vector Store:** Amazon OpenSearch")
    st.markdown("- **Infrastructure:** Terraform")
    st.markdown("- **Security:** IAM / Boto3 SigV4")

# --- Main Page UI ---
st.title("🤖 Enterprise HR Knowledge Assistant")
st.markdown("Query company policy documents securely using a verified **RAG Pipeline** powered by Amazon Bedrock.")
st.caption("🔒 Engineered and deployed by **Syed Taher** | Enterprise VPC/S3 Framework")
st.divider()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📄 Viewed Sources"):
                for source in message["sources"]:
                    st.markdown(f"- `{source}`")

# Accept user input
if user_query := st.chat_input("Ask a question about PTO, remote work, or travel policies..."):
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display assistant response container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.spinner("Analyzing knowledge base..."):
            answer, sources = query_bedrock_rag(user_query)
            
        response_placeholder.markdown(answer)
        
        # If sources are returned, display them neatly in an expander drop-down
        if sources:
            with st.expander("📄 Viewed Sources"):
                for source in sources:
                    st.markdown(f"- `{source}`")
                    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "sources": sources
    })
