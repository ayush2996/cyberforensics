# semantic_router.py
"""
Stage One: Embedding-Based Semantic Router
Performs high-speed vector matching against crime clusters using cosine similarity.
"""

from embeddings_manager import embeddings_manager
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class CrimeCluster:
    """Represents a crime type cluster with example descriptions"""
    name: str
    description: str
    keywords: List[str]
    embedding: List[float] = None
    
    async def compute_embedding(self):
        """Compute embedding for the cluster description"""
        if self.embedding is None:
            embeddings = await embeddings_manager.embed_texts([self.description])
            self.embedding = embeddings[0]

class SemanticRouter:
    """
    Routes incident reports to crime types using embedding-based semantic similarity.
    Uses cosine similarity to match user input against pre-defined crime clusters.
    """
    
    def __init__(self):
        """Initialize crime clusters with descriptions and keywords"""
        self.clusters = {
            "phishing": CrimeCluster(
                name="Phishing",
                description="Deceptive emails or messages that trick users into revealing credentials, clicking malicious links, or downloading malware. Examples: fake bank login pages, credential harvesting, social engineering via email",
                keywords=["email", "link", "click", "verify", "account", "password", "credential", "fake", "urgent", "confirm"]
            ),
            "ransomware": CrimeCluster(
                name="Ransomware",
                description="Malicious software that encrypts files and demands payment for recovery. Files become inaccessible with encrypted extensions. Ransom notes demand payment in cryptocurrency",
                keywords=["encrypted", "ransom", "locked", "pay", "bitcoin", "wallet", "recovery", "extension", "note", "deadline"]
            ),
            "data_breach": CrimeCluster(
                name="Data Breach",
                description="Unauthorized access to confidential databases containing customer records, financial information, or sensitive data. Attackers steal or expose large volumes of data",
                keywords=["breach", "accessed", "database", "records", "stolen", "exposed", "organization", "unauthorized", "access", "data"]
            ),
            "identity_theft": CrimeCluster(
                name="Identity Theft",
                description="Fraudulent use of someone's personal information to open accounts, make purchases, or obtain credit. Victims discover unauthorized accounts and financial damage",
                keywords=["identity", "ssn", "credit", "account", "opened", "fraudulent", "fraud", "victim", "personal", "information"]
            ),
            "fraud": CrimeCluster(
                name="Fraud",
                description="Deceptive financial schemes including wire fraud, credit card fraud, investment scams, or fake payment schemes to steal money from victims",
                keywords=["fraud", "scam", "money", "transfer", "payment", "wire", "card", "credit", "victim", "lost"]
            ),
            "malware": CrimeCluster(
                name="Malware",
                description="Malicious software infections including trojans, worms, spyware, and rootkits that compromise system security and steal data or enable unauthorized access",
                keywords=["malware", "virus", "infection", "spyware", "trojan", "antivirus", "detected", "quarantine", "installed", "suspicious"]
            ),
            "ddos": CrimeCluster(
                name="DDoS Attack",
                description="Distributed denial of service attacks that overwhelm servers with traffic to make websites unavailable. Targets specific services or websites",
                keywords=["ddos", "attack", "unavailable", "down", "service", "traffic", "overwhelming", "denial", "offline", "server"]
            ),
            "hacking": CrimeCluster(
                name="Unauthorized Access/Hacking",
                description="Unauthorized system access through brute force, exploitation, or social engineering. Attackers gain control of accounts or systems",
                keywords=["hacking", "access", "unauthorized", "breach", "intrusion", "account", "compromised", "system", "backdoor", "exploit"]
            ),
            "extortion": CrimeCluster(
                name="Extortion/Blackmail",
                description="Criminal threats demanding money, action, or favors under penalty of harm, data exposure, or violence. Perpetrators claim to have damaging information",
                keywords=["extortion", "threat", "blackmail", "demand", "payment", "expose", "harm", "data", "ransom", "evidence"]
            ),
            "spam": CrimeCluster(
                name="Spam",
                description="Unsolicited bulk messages including emails, SMS, or social media messages. Often phishing, scam, or malware distribution vectors",
                keywords=["spam", "unsolicited", "message", "bulk", "email", "sms", "social", "media", "suspicious", "unknown"]
            ),
        }
        self.initialized = False
    
    async def initialize(self):
        """Pre-compute embeddings for all clusters (expensive operation, do once)"""
        if self.initialized:
            return
        
        print("[*] Initializing semantic router... computing cluster embeddings...")
        for crime_type, cluster in self.clusters.items():
            await cluster.compute_embedding()
            print(f"    [+] {cluster.name}")
        
        self.initialized = True
        print("[OK] Semantic router ready!")
    
    async def route(self, user_input: str, top_k: int = 3) -> Dict:
        """
        Route user input to most similar crime clusters.
        
        Args:
            user_input: The incident description from user
            top_k: Return top K matches
            
        Returns:
            Dict with similarities, rankings, and top match
        """
        if not self.initialized:
            await self.initialize()
        
        # Embed user input
        user_embedding = await embeddings_manager.embed_query(user_input)
        
        # Calculate cosine similarity with all clusters
        similarities = {}
        for crime_type, cluster in self.clusters.items():
            if cluster.embedding is None:
                await cluster.compute_embedding()
            
            # Cosine similarity: dot(a,b) / (||a|| * ||b||)
            user_emb_arr = np.array(user_embedding)
            cluster_emb_arr = np.array(cluster.embedding)
            
            dot_product = np.dot(user_emb_arr, cluster_emb_arr)
            user_norm = np.linalg.norm(user_emb_arr)
            cluster_norm = np.linalg.norm(cluster_emb_arr)
            
            cosine_sim = dot_product / (user_norm * cluster_norm) if user_norm > 0 and cluster_norm > 0 else 0
            similarities[crime_type] = cosine_sim
        
        # Sort by similarity
        ranked = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate gap between top 2 (confidence metric)
        top_gap = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else ranked[0][1]
        
        return {
            "all_similarities": dict(ranked),
            "top_k_matches": ranked[:top_k],
            "primary_match": ranked[0][0],
            "primary_similarity": ranked[0][1],
            "confidence_gap": top_gap,  # >0.8 is high confidence
            "high_confidence": top_gap > 0.8,
            "user_embedding": user_embedding
        }
    
    def get_keyword_match_score(self, user_input: str, crime_type: str) -> float:
        """
        Calculate keyword overlap score for a crime type.
        
        Args:
            user_input: User's incident description
            crime_type: Target crime type
            
        Returns:
            Float 0-1 representing keyword match percentage
        """
        if crime_type not in self.clusters:
            return 0.0
        
        cluster = self.clusters[crime_type]
        user_words = set(user_input.lower().split())
        cluster_keywords = set(kw.lower() for kw in cluster.keywords)
        
        if not cluster_keywords:
            return 0.0
        
        matches = user_words & cluster_keywords
        score = len(matches) / len(cluster_keywords)
        return min(score, 1.0)  # Cap at 1.0
    
    async def multi_stage_route(self, user_input: str) -> Dict:
        """
        Combine embedding similarity with keyword matching.
        
        Returns:
            Enhanced routing result
        """
        embedding_route = await self.route(user_input)
        
        # Add keyword scores
        keyword_scores = {}
        for crime_type in self.clusters.keys():
            keyword_scores[crime_type] = self.get_keyword_match_score(user_input, crime_type)
        
        # Combine scores (70% embedding, 30% keywords)
        combined_scores = {}
        for crime_type in self.clusters.keys():
            emb_score = dict(embedding_route["all_similarities"])[crime_type]
            kw_score = keyword_scores[crime_type]
            combined_scores[crime_type] = (0.7 * emb_score) + (0.3 * kw_score)
        
        # Re-rank by combined score
        ranked_combined = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            **embedding_route,
            "keyword_scores": keyword_scores,
            "combined_scores": dict(ranked_combined),
            "final_ranking": ranked_combined,
            "primary_match": ranked_combined[0][0],
            "primary_score": ranked_combined[0][1]
        }

# Singleton instance
semantic_router = SemanticRouter()

