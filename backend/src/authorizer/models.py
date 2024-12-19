import json
import re
import xml.sax.saxutils
from datetime import datetime
from html import unescape
from typing import Any, Dict, List, Optional

from dateutil import parser
from flask import jsonify
from pydantic import BaseModel, HttpUrl


class TwitterFeedProcessor:
    """Processes Twitter feed data into ContentItem format"""
    
    def _extract_urls(self, tweet: Dict[str, Any]) -> tuple[str, Optional[List[HttpUrl]]]:
        """Extract URLs from tweet and return cleaned text and list of URLs"""
        text = tweet["full_text"]
        embedded_urls = []
        
        entities = tweet.get("entities", {})
        
        # Process URLs
        if "urls" in entities:
            for url_dict in entities["urls"]:
                if not url_dict["expanded_url"].startswith("https://twitter.com/"):
                    embedded_urls.append(url_dict["expanded_url"])
                text = text.replace(url_dict["url"], "")
        
        # Process media URLs
        if "media" in entities:
            for media in entities["media"]:
                media_url = media["media_url"].replace("http:", "https:")
                embedded_urls.append(media_url)
                if "url" in media:
                    text = text.replace(media["url"], "")
        
        return text.strip(), embedded_urls if embedded_urls else None

    def _create_engagements(self, tweet: Dict[str, Any]) -> TwitterEngagements:
        """Create TwitterEngagements object from tweet data"""
        return TwitterEngagements(
            retweet=tweet["retweet_count"],
            like=tweet["favorite_count"],
            comment=0,  # Reply count not available in current tweet format
            share=0     # Share count not available in current tweet format
        )

    def process_tweet(self, tweet: Dict[str, Any], rank: int) -> ContentItem:
        """Process a single tweet into a ContentItem"""
        # Extract text and URLs
        clean_text, embedded_urls = self._extract_urls(tweet)
        
        # Determine if it's a reply
        is_reply = bool(tweet.get("in_reply_to_status_id_str"))
        
        # Create ContentItem
        return ContentItem(
            id=tweet["id_str"],
            original_rank=rank,
            text=unescape(clean_text),
            author_name_hash=tweet["user"]["screen_name"],  # Using screen_name as hash
            type="comment" if is_reply else "post",
            embedded_urls=embedded_urls,
            created_at=parser.parse(tweet["created_at"]),
            engagements=self._create_engagements(tweet),
            language=tweet.get("lang"),
            # Optional fields defaulting to None:
            post_id=None,
            parent_id=tweet.get("in_reply_to_status_id_str"),
            title=None
        )
