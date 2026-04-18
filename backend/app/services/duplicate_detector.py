"""
Enhanced Duplicate Detection Service
Provides detailed similarity analysis and reasoning
"""
from typing import List, Dict, Any
import numpy as np
from app.services.vector_service import find_similar_issues


class DuplicateDetector:
    """Advanced duplicate detection with reasoning"""
    
    def __init__(self):
        self.similarity_thresholds = {
            "definite": 0.90,  # 90%+ = definite duplicate
            "likely": 0.70,    # 70-89% = likely duplicate
            "possible": 0.50,  # 50-69% = possibly related
            "related": 0.30    # 30-49% = loosely related
        }
    
    def analyze_duplicates(
        self,
        title: str,
        description: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Comprehensive duplicate analysis with reasoning
        
        Returns:
            - similar_issues: List of similar issues with scores
            - duplicate_level: definite/likely/possible/none
            - reasoning: Why these are considered duplicates
            - confidence: Overall confidence score
            - clusters: Grouped by similarity level
        """
        
        # Find similar issues
        similar = find_similar_issues(title, description, top_k=top_k)
        
        if not similar:
            return {
                "similar_issues": [],
                "duplicate_level": "none",
                "reasoning": "No similar issues found. This appears to be a unique issue.",
                "confidence": 1.0,
                "clusters": {
                    "definite": [],
                    "likely": [],
                    "possible": [],
                    "related": []
                },
                "statistics": {
                    "total_similar": 0,
                    "highest_similarity": 0,
                    "average_similarity": 0
                }
            }
        
        # Categorize by similarity level
        clusters = self._categorize_by_similarity(similar)
        
        # Determine duplicate level
        duplicate_level = self._determine_duplicate_level(clusters)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            title, description, similar, clusters, duplicate_level
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(similar, clusters)
        
        # Calculate statistics
        similarities = [s.get("similarity_score", 0) for s in similar]
        statistics = {
            "total_similar": len(similar),
            "highest_similarity": max(similarities) if similarities else 0,
            "average_similarity": np.mean(similarities) if similarities else 0,
            "definite_count": len(clusters["definite"]),
            "likely_count": len(clusters["likely"]),
            "possible_count": len(clusters["possible"]),
            "related_count": len(clusters["related"])
        }
        
        return {
            "similar_issues": similar,
            "duplicate_level": duplicate_level,
            "reasoning": reasoning,
            "confidence": confidence,
            "clusters": clusters,
            "statistics": statistics
        }
    
    def _categorize_by_similarity(self, similar: List[Dict]) -> Dict[str, List]:
        """Group issues by similarity level"""
        clusters = {
            "definite": [],
            "likely": [],
            "possible": [],
            "related": []
        }
        
        for issue in similar:
            score = issue.get("similarity_score", 0)
            
            if score >= self.similarity_thresholds["definite"]:
                clusters["definite"].append(issue)
            elif score >= self.similarity_thresholds["likely"]:
                clusters["likely"].append(issue)
            elif score >= self.similarity_thresholds["possible"]:
                clusters["possible"].append(issue)
            elif score >= self.similarity_thresholds["related"]:
                clusters["related"].append(issue)
        
        return clusters
    
    def _determine_duplicate_level(self, clusters: Dict[str, List]) -> str:
        """Determine overall duplicate level"""
        if clusters["definite"]:
            return "definite"
        elif clusters["likely"]:
            return "likely"
        elif clusters["possible"]:
            return "possible"
        elif clusters["related"]:
            return "related"
        return "none"
    
    def _generate_reasoning(
        self,
        title: str,
        description: str,
        similar: List[Dict],
        clusters: Dict[str, List],
        duplicate_level: str
    ) -> str:
        """Generate human-readable reasoning for duplicate detection"""
        
        if duplicate_level == "none":
            return "No similar issues found. This appears to be a unique issue."
        
        reasoning_parts = []
        
        # Main finding
        if duplicate_level == "definite":
            count = len(clusters["definite"])
            reasoning_parts.append(
                f"Found {count} definite duplicate{'s' if count > 1 else ''} "
                f"(90%+ similarity)."
            )
        elif duplicate_level == "likely":
            count = len(clusters["likely"])
            reasoning_parts.append(
                f"Found {count} likely duplicate{'s' if count > 1 else ''} "
                f"(70-89% similarity)."
            )
        elif duplicate_level == "possible":
            count = len(clusters["possible"])
            reasoning_parts.append(
                f"Found {count} possibly related issue{'s' if count > 1 else ''} "
                f"(50-69% similarity)."
            )
        else:
            count = len(clusters["related"])
            reasoning_parts.append(
                f"Found {count} loosely related issue{'s' if count > 1 else ''} "
                f"(30-49% similarity)."
            )
        
        # Analyze common patterns
        if similar:
            top_match = similar[0]
            top_score = top_match.get("similarity_score", 0) * 100
            top_title = top_match.get("title", "Unknown")
            
            reasoning_parts.append(
                f"Highest match: '{top_title}' ({top_score:.0f}% similar)."
            )
        
        # Semantic analysis
        common_keywords = self._extract_common_keywords(title, description, similar)
        if common_keywords:
            reasoning_parts.append(
                f"Common themes: {', '.join(common_keywords[:3])}."
            )
        
        # Recommendation
        if duplicate_level == "definite":
            reasoning_parts.append(
                "Recommendation: Review these issues before proceeding. "
                "This may be a duplicate that can be closed."
            )
        elif duplicate_level == "likely":
            reasoning_parts.append(
                "Recommendation: Check if this issue adds new information "
                "or can be merged with existing ones."
            )
        
        return " ".join(reasoning_parts)
    
    def _extract_common_keywords(
        self,
        title: str,
        description: str,
        similar: List[Dict]
    ) -> List[str]:
        """Extract common keywords from similar issues"""
        # Simple keyword extraction (can be enhanced with NLP)
        current_words = set(title.lower().split())
        
        keyword_counts = {}
        for issue in similar[:3]:  # Top 3
            issue_title = issue.get("title", "").lower()
            for word in issue_title.split():
                if len(word) > 3 and word in current_words:
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [kw for kw, _ in sorted_keywords[:5]]
    
    def _calculate_confidence(
        self,
        similar: List[Dict],
        clusters: Dict[str, List]
    ) -> float:
        """Calculate confidence score for duplicate detection"""
        if not similar:
            return 1.0  # 100% confident there are no duplicates
        
        # Factors affecting confidence:
        # 1. Number of similar issues
        # 2. Similarity scores
        # 3. Consistency of scores
        
        similarities = [s.get("similarity_score", 0) for s in similar]
        
        # High similarity = high confidence
        max_sim = max(similarities) if similarities else 0
        
        # Multiple similar issues = higher confidence
        count_factor = min(len(similar) / 5, 1.0)  # Cap at 5 issues
        
        # Consistent scores = higher confidence
        if len(similarities) > 1:
            std_dev = np.std(similarities)
            consistency_factor = 1.0 - min(std_dev, 0.3)
        else:
            consistency_factor = 0.8
        
        # Weighted average
        confidence = (
            max_sim * 0.5 +
            count_factor * 0.3 +
            consistency_factor * 0.2
        )
        
        return min(confidence, 0.99)  # Cap at 99%


# Global instance
duplicate_detector = DuplicateDetector()
