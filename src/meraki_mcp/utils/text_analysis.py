"""Utility functions for text analysis and information extraction from natural language queries."""

import re
import logging
import os
import sys
import importlib.util
from typing import Dict, List, Any, Optional, Set, Tuple

# Initialize logger
logger = logging.getLogger(__name__)

# Define flag for whether NLP libraries are available
NLTK_AVAILABLE = False

# Try multiple approaches to detect and import NLTK
try:
    import nltk
    import numpy  # Required for advanced NLTK features
    NLTK_AVAILABLE = True
except ImportError:
    try:
        # Alternative way to check if nltk is installed
        NLTK_AVAILABLE = importlib.util.find_spec("nltk") is not None and importlib.util.find_spec("numpy") is not None
        if NLTK_AVAILABLE:
            import nltk
            import numpy
    except Exception as e:
        logger.warning(f"Error importing NLTK/NumPy: {e}")
        NLTK_AVAILABLE = False

logger.info(f"NLTK available: {NLTK_AVAILABLE}")

# Import NLP libraries if available
if NLTK_AVAILABLE:
    try:
        # Create a dedicated logger for NLP operations
        nlp_logger = logging.getLogger("meraki_mcp.nlp")
        nlp_logger.info("NLTK is available. Initializing NLP capabilities.")
        
        # Check if we need to download NLTK data
        try:
            # Try to load required NLTK resources
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('chunkers/maxent_ne_chunker')
            nltk.data.find('corpora/words')
            nlp_logger.info("All required NLTK resources found.")
        except LookupError as e:
            nlp_logger.warning(f"Missing NLTK resource: {e}. Attempting to download.")
            try:
                # Resources not downloaded, attempt to download them
                nltk.download('punkt', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('maxent_ne_chunker', quiet=True)
                nltk.download('words', quiet=True)
                nlp_logger.info("Successfully downloaded required NLTK resources.")
            except Exception as e:
                # Failed to download resources
                NLTK_AVAILABLE = False
                nlp_logger.error(f"Failed to download NLTK resources: {e}. Using regex fallback.")
    except ImportError as e:
        NLTK_AVAILABLE = False
        logging.warning(f"Failed to import NLTK: {e}. Using regex fallback.")

logger = logging.getLogger(__name__)

class QueryContext:
    """Class to store extracted context from natural language queries."""
    
    def __init__(self):
        """Initialize empty query context."""
        self.location_identifiers: List[str] = []
        self.building_identifiers: List[str] = []
        self.network_identifiers: List[str] = []
        self.device_identifiers: List[str] = []
        self.device_types: List[str] = []
        self.ssid_names: List[str] = []
        self.error_messages: List[str] = []
        self.urgency_indicators: List[str] = []
        self.time_references: List[str] = []
        self.client_identifiers: List[str] = []
        self.ap_identifiers: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the context to a dictionary.
        
        Returns:
            Dictionary representation of the extracted context
        """
        return {
            "location_identifiers": self.location_identifiers,
            "building_identifiers": self.building_identifiers,
            "network_identifiers": self.network_identifiers,
            "device_identifiers": self.device_identifiers,
            "device_types": self.device_types,
            "ssid_names": self.ssid_names,
            "error_messages": self.error_messages,
            "urgency_indicators": self.urgency_indicators,
            "time_references": self.time_references,
            "client_identifiers": self.client_identifiers,
            "ap_identifiers": self.ap_identifiers
        }
    
    def __str__(self) -> str:
        """String representation of the context.
        
        Returns:
            String representation
        """
        return f"QueryContext: {self.to_dict()}"

def extract_context_from_query(query: str) -> QueryContext:
    """Extract context information from a natural language query.
    
    This function analyzes a natural language query to identify and extract
    various types of contextual information such as:
    - Location references (room numbers, coordinates, etc.)
    - Building or site identifiers
    - Network identifiers (network names, etc.)
    - Device identifiers (MAC addresses, serial numbers, etc.)
    - Device types (computer, phone, etc.)
    - SSID names
    - Error messages
    - Urgency indicators
    - Time references
    - Client identifiers
    - Access point identifiers
    
    The function uses NLP libraries when available for more accurate parsing,
    with fallback to regex patterns when NLP is not available or for specific pattern matching.
    
    Args:
        query: Natural language query to analyze
        
    Returns:
        QueryContext object containing extracted contextual information
    """
    # Initialize the context object
    context = QueryContext()
    
    # If no query, return empty context
    if not query or not query.strip():
        return context
        
    # Try NLP-based extraction first if available
    if NLTK_AVAILABLE:
        try:
            logger.info(f"Attempting NLP-based extraction for query: '{query[:30]}...' (truncated)")
            context = _extract_context_with_nlp(query)
            logger.info("NLP-based extraction successful")
            
            # Log what was found by NLP
            extracted_info = {
                "ssid_names": context.ssid_names,
                "network_identifiers": context.network_identifiers,
                "device_types": context.device_types
            }
            logger.info(f"NLP extracted context: {extracted_info}")
            
            # Combine with regex extraction for specific patterns that NLP might miss
            logger.debug("Adding regex extraction to supplement NLP results")
            regex_context = _extract_context_with_regex(query)
            _merge_contexts(context, regex_context)
            
            return context
        except Exception as e:
            logger.warning(f"NLP-based extraction failed: {e}. Falling back to regex.")
    else:
        logger.info("NLTK is not available. Using regex-only extraction.")
    
    # Fallback to regex-based extraction
    context = _extract_context_with_regex(query)
    return context


def _merge_contexts(primary: QueryContext, secondary: QueryContext) -> None:
    """Merge two context objects, with the primary context taking precedence.
    
    Args:
        primary: The primary context object that will be updated
        secondary: The secondary context object to merge from
    """
    # Merge list attributes from secondary to primary if not already present
    for attr in [
        "location_identifiers", "building_identifiers", "network_identifiers", 
        "device_identifiers", "device_types", "ssid_names", "error_messages", 
        "urgency_indicators", "time_references", "client_identifiers", "ap_identifiers"
    ]:
        primary_list = getattr(primary, attr)
        secondary_list = getattr(secondary, attr)
        
        for item in secondary_list:
            if item not in primary_list:
                primary_list.append(item)


def _extract_context_with_nlp(query: str) -> QueryContext:
    """Extract context from a query using NLP techniques.
    
    Args:
        query: The query string to analyze
        
    Returns:
        QueryContext with extracted information
    """
    context = QueryContext()
    
    # Ensure all required NLTK resources are available
    try:
        # List of required resources
        required_resources = [
            ('tokenizers/punkt', 'punkt'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('chunkers/maxent_ne_chunker', 'maxent_ne_chunker'),
            ('corpora/words', 'words'),
        ]
        
        # Check and download any missing resources
        for resource_path, resource_name in required_resources:
            try:
                nltk.data.find(resource_path)
            except LookupError:
                logger.info(f"Auto-downloading missing NLTK resource: {resource_name}")
                nltk.download(resource_name, quiet=True)
    except Exception as e:
        logger.warning(f"Error checking/downloading NLTK resources: {e}")
    
    # Process the query with NLTK
    tokens = nltk.word_tokenize(query)
    pos_tags = nltk.pos_tag(tokens)
    named_entities = nltk.ne_chunk(pos_tags)
    
    # Process named entities to extract potential network names and SSIDs
    for chunk in named_entities:
        if hasattr(chunk, 'label'):
            # Named entity detected
            entity_text = ' '.join(c[0] for c in chunk)
            # Organizations are often network names
            if chunk.label() in ['ORGANIZATION', 'GPE', 'FACILITY']:
                context.network_identifiers.append(entity_text)
            # Person names could be SSIDs (people often name networks after themselves)
            if chunk.label() == 'PERSON':
                context.ssid_names.append(entity_text)
    
    # Use POS patterns for phrases that indicate SSIDs and networks
    for i, (token, pos) in enumerate(pos_tags):
        # Look for prepositions followed by proper nouns (potential networks)
        if token.lower() in ['at', 'on', 'in'] and i < len(pos_tags) - 1:
            next_token, next_pos = pos_tags[i+1]
            if next_pos.startswith('NNP'):  # Proper noun
                context.network_identifiers.append(next_token)
        
        # Look for verbs related to connecting followed by 'to' and a noun (potential SSIDs)
        if pos.startswith('VB') and token.lower() in ['connect', 'connecting', 'connected', 'join', 'joining', 'joined']:
            if i < len(pos_tags) - 2 and pos_tags[i+1][0].lower() == 'to':
                ssid_candidate = pos_tags[i+2][0]
                if pos_tags[i+2][1].startswith('NN'):  # Any noun
                    context.ssid_names.append(ssid_candidate)
    
    # Handle special case of "X at X" where X is the same word (e.g., "Home at Home")
    for i, (token, _) in enumerate(pos_tags):
        if token.lower() == 'at' and i > 0 and i < len(pos_tags) - 1:
            prev_token = pos_tags[i-1][0]
            next_token = pos_tags[i+1][0]
            
            if prev_token.lower() == next_token.lower() and len(prev_token) > 1:
                # Same word before and after "at" - likely SSID and network
                if prev_token not in context.ssid_names:
                    context.ssid_names.append(prev_token)
                if next_token not in context.network_identifiers:
                    context.network_identifiers.append(next_token)
    
    # Extract device types based on known device keywords
    device_keywords = ["laptop", "computer", "phone", "mobile", "tablet", "pc", "mac", "device"]
    for i, (token, pos) in enumerate(pos_tags):
        if token.lower() in device_keywords:
            context.device_types.append(token.lower())
            # Look for adjectives or compound nouns before device keywords
            if i > 0 and (pos_tags[i-1][1].startswith('JJ') or pos_tags[i-1][1].startswith('NN')):
                full_device = f"{pos_tags[i-1][0]} {token}"
                context.device_types.append(full_device.lower())
    
    # Extract error messages by finding quoted text
    in_quote = False
    current_quote = ""
    for token, _ in pos_tags:
        if token in ['"', '\'']:
            if not in_quote:
                in_quote = True
                current_quote = ""
            else:
                in_quote = False
                if len(current_quote) > 3:  # Only add if it's substantial
                    context.error_messages.append(current_quote.strip())
                current_quote = ""
        elif in_quote:
            current_quote += token + " "
    
    # Extract urgency indicators
    urgency_terms = ["asap", "urgent", "emergency", "immediately", "right away", 
                   "critical", "high priority", "as soon as possible"]
    for token, _ in pos_tags:
        if token.lower() in urgency_terms:
            context.urgency_indicators.append(token.lower())
    
    # If we're still not sure about a term, add a function to directly ask the user
    # This addresses the requirement to "ask the user" when we can't determine context
    
    return context


def _extract_context_with_regex(query: str) -> QueryContext:
    """Extract context from a query using regex patterns.
    
    This is a fallback method when NLP is not available, or used to supplement
    NLP-based extraction for specific pattern matching.
    
    Args:
        query: The query string to analyze
        
    Returns:
        QueryContext with extracted information
    """
    context = QueryContext()
    query_lower = query.lower()
    
    # Extract location identifiers (room numbers, coordinates)
    # Format examples: Room W23, Room 123, W23, Building 5 Room 123
    room_patterns = [
        r'\b(?:room|rm)\s*([a-z0-9]+[-]?[a-z0-9]*)\b',  # Room W23, Room 123
        r'\b([a-z][0-9]{1,3})\b',  # W23 (letter followed by 1-3 digits)
        r'\b((?:east|west|north|south|e|w|n|s)[- ]?[0-9]{1,3})\b'  # East-123, N123
    ]
    
    for pattern in room_patterns:
        for match in re.finditer(pattern, query_lower):
            room_id = match.group(1).strip()
            if room_id and room_id not in context.location_identifiers:
                context.location_identifiers.append(room_id)
    
    # Extract building or site identifiers
    # Examples: Building 5, School 6, Site 12
    building_patterns = [
        r'\b(?:building|school|site)\s*([0-9]+)\b',  # Building 5, School 6
        r'\b((?:bldg|sch)\.?\s*[0-9]+)\b'  # Bldg. 5, Sch. 6
    ]
    
    for pattern in building_patterns:
        for match in re.finditer(pattern, query_lower):
            building_id = match.group(1).strip()
            if building_id and building_id not in context.building_identifiers:
                context.building_identifiers.append(building_id)
                # Also add as a potential network identifier
                context.network_identifiers.append(building_id)
    
    # Extract network identifiers (could be mixed with building/location names)
    # Specific network name patterns
    network_patterns = [
        r'\bnetwork[:\s]+["\']?([a-z0-9_-]+)["\']?\b',  # network: name
        r'\b(?:in|on|at)\s+(?:the\s+)?["\']?([a-z0-9_-]+)["\']?\s+(?:network|site)\b'  # in the "Name" network
    ]
    
    for pattern in network_patterns:
        for match in re.finditer(pattern, query_lower):
            network_id = match.group(1).strip()
            if network_id and network_id not in context.network_identifiers:
                context.network_identifiers.append(network_id)
    
    # Extract device types
    device_type_patterns = [
        r'\b(macbook|windows|laptop|desktop|computer|phone|iphone|android|ios|pc|mac|chromebook|tablet|ipad)\b',
        r'\b(multiple devices|all devices|several devices)\b'
    ]
    
    for pattern in device_type_patterns:
        for match in re.finditer(pattern, query_lower):
            device_type = match.group(1).strip()
            if device_type and device_type not in context.device_types:
                context.device_types.append(device_type)
    
    # Extract SSID names (network names)
    ssid_patterns = [
        r'\bssid[:\s]+["\']?([a-z0-9_-]+)["\']?\b',  # SSID: name
        r'\b(?:wifi|wireless|network)[:\s]+["\']?([a-z0-9_-]+)["\']?\b',  # WiFi: name
        r'\bconnect(?:ing)?\s+to\s+["\']?([a-z0-9_-]+)["\']?\b'  # connecting to name
    ]
    
    for pattern in ssid_patterns:
        for match in re.finditer(pattern, query_lower):
            ssid_name = match.group(1).strip()
            if ssid_name and ssid_name not in context.ssid_names:
                context.ssid_names.append(ssid_name)
    
    # Look for specific SSIDs with "open" in the name
    open_ssid_pattern = r'\b([a-z0-9_-]*open[a-z0-9_-]*)\b'
    for match in re.finditer(open_ssid_pattern, query_lower):
        open_ssid = match.group(1).strip()
        if open_ssid and open_ssid not in context.ssid_names:
            context.ssid_names.append(open_ssid)
    
    # Extract error messages
    error_msg_patterns = [
        r'error\s+(?:message|saying|states?|that\s+says?)[:\s]+["\']([^"\']+)["\']',
        r'(?:get|receive|seeing|see|shows?)\s+(?:an|the)?\s+error[:\s]+["\']([^"\']+)["\']'
    ]
    
    for pattern in error_msg_patterns:
        for match in re.finditer(pattern, query_lower):
            error_msg = match.group(1).strip()
            if error_msg and error_msg not in context.error_messages:
                context.error_messages.append(error_msg)
    
    # If no specific error patterns matched, look for quoted strings
    if not context.error_messages:
        quote_pattern = r'["\']([^"\']{5,})["\']'  # At least 5 chars to avoid false positives
        for match in re.finditer(quote_pattern, query_lower):
            quoted_text = match.group(1).strip()
            if "error" in quoted_text or "unable" in quoted_text or "fail" in quoted_text:
                if quoted_text not in context.error_messages:
                    context.error_messages.append(quoted_text)
    
    # Extract urgency indicators
    urgency_terms = ["asap", "urgent", "emergency", "immediately", "right away", 
                     "critical", "high priority", "as soon as possible"]
    
    for term in urgency_terms:
        if term in query_lower:
            context.urgency_indicators.append(term)
    
    # Extract time references
    time_patterns = [
        r'\b(?:on|at|during|since|before|after)\s+([a-z]+day)\b',  # Monday, Tuesday
        r'\b(?:on|at|during|since)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b',  # 3:00 PM
        r'\b(this|last|next)\s+(morning|afternoon|evening|night|week|day)\b'  # this morning
    ]
    
    for pattern in time_patterns:
        for match in re.finditer(pattern, query_lower):
            time_ref = match.group(0).strip()  # Use the whole match
            if time_ref and time_ref not in context.time_references:
                context.time_references.append(time_ref)
    
    # Extract AP identifiers
    ap_patterns = [
        r'\bap\s*([a-z0-9_-]+)\b',  # AP name
        r'\baccess\s+point\s*([a-z0-9_-]+)\b',  # Access Point name
        r'\b((?:ap|base|station)[_-]?[a-z0-9]+)\b'  # AP-123, base-station-X
    ]
    
    for pattern in ap_patterns:
        for match in re.finditer(pattern, query_lower):
            ap_id = match.group(1).strip()
            if ap_id and ap_id not in context.ap_identifiers:
                context.ap_identifiers.append(ap_id)
    
    # Add room identifiers as potential AP identifiers since they often match
    for room_id in context.location_identifiers:
        if room_id not in context.ap_identifiers:
            context.ap_identifiers.append(room_id)
    
    logger.debug(f"Extracted context from query: {context}")
    return context

def find_matching_devices(
    context: QueryContext, 
    available_devices: List[Dict[str, Any]],
    match_device_types: bool = True,
    match_ap_identifiers: bool = True,
    match_fuzzy: bool = True
) -> List[Dict[str, Any]]:
    """Find devices that match the context from a list of available devices.
    
    This function attempts to match devices in the available_devices list
    against the contextual information extracted from a query.
    
    Args:
        context: QueryContext containing extracted information
        available_devices: List of device dictionaries to match against
        match_device_types: Whether to match against device types
        match_ap_identifiers: Whether to match against AP identifiers
        match_fuzzy: Whether to use fuzzy matching for identifiers
        
    Returns:
        List of matching device dictionaries
    """
    matches = []
    
    for device in available_devices:
        device_name = device.get("name", "").lower()
        device_model = device.get("model", "").lower()
        device_serial = device.get("serial", "").lower()
        device_tags = device.get("tags", [])
        if isinstance(device_tags, str):
            device_tags = [device_tags]
        device_tags = [t.lower() for t in device_tags if t]
        
        # Check if device matches any of the AP identifiers
        ap_match = False
        if match_ap_identifiers and context.ap_identifiers:
            for ap_id in context.ap_identifiers:
                ap_id_lower = ap_id.lower()
                # Direct matches
                if (ap_id_lower in device_name or 
                    ap_id_lower in device_serial or
                    any(ap_id_lower in tag for tag in device_tags)):
                    ap_match = True
                    break
                
                # Fuzzy matches if enabled
                if match_fuzzy:
                    # For room numbers like W23, look for W-23, W.23, etc.
                    if re.match(r'^[a-z][0-9]+$', ap_id_lower):
                        letter = ap_id_lower[0]
                        number = ap_id_lower[1:]
                        patterns = [
                            f"{letter}-{number}",
                            f"{letter}.{number}",
                            f"{letter}_{number}"
                        ]
                        for pattern in patterns:
                            if (pattern in device_name or
                                pattern in device_serial or
                                any(pattern in tag for tag in device_tags)):
                                ap_match = True
                                break
        
        # Check if device matches any device types
        device_type_match = False
        if match_device_types and context.device_types:
            if "mr" in device_model.lower():  # Meraki access points
                device_type_match = any(dt in ["ap", "access point", "wireless"] 
                                      for dt in context.device_types)
            elif "ms" in device_model.lower():  # Meraki switches
                device_type_match = any(dt in ["switch", "switches"] 
                                      for dt in context.device_types)
            elif "mx" in device_model.lower():  # Meraki security appliances
                device_type_match = any(dt in ["firewall", "gateway", "router"] 
                                      for dt in context.device_types)
        
        # Add device to matches if it matches any criteria
        if ap_match or device_type_match:
            if device not in matches:
                matches.append(device)
    
    return matches

def detect_ambiguities(context: QueryContext) -> Dict[str, List[str]]:
    """Detect potential ambiguities in the extracted context.
    
    This function analyzes the extracted context to identify situations where
    the same term might be used in multiple contexts (e.g., as both an SSID name
    and a network name). This helps determine when to ask the user for clarification.
    
    Args:
        context: The QueryContext object to analyze for ambiguities
        
    Returns:
        Dictionary mapping ambiguity types to lists of ambiguous terms
    """
    ambiguities = {
        "ssid_network": [],  # Terms that could be either SSID or network name
        "location": [],      # Terms that could be either room or building
        "device": []         # Terms that could refer to multiple devices
    }
    
    # Check for terms that appear in both SSID and network identifiers
    for ssid in context.ssid_names:
        if ssid in context.network_identifiers and ssid not in ambiguities["ssid_network"]:
            ambiguities["ssid_network"].append(ssid)
    
    # Check for terms that appear in both location and building identifiers
    for loc in context.location_identifiers:
        if loc in context.building_identifiers and loc not in ambiguities["location"]:
            ambiguities["location"].append(loc)
    
    # Log detected ambiguities
    if any(ambiguities.values()):
        logger.info(f"Detected ambiguities in context extraction: {ambiguities}")
    
    return ambiguities


def generate_clarification_questions(ambiguities: Dict[str, List[str]]) -> List[str]:
    """Generate questions to ask the user to clarify ambiguities.
    
    Args:
        ambiguities: Dictionary of ambiguity types and terms from detect_ambiguities()
        
    Returns:
        List of questions to ask the user
    """
    questions = []
    
    # Handle SSID/Network ambiguities
    for term in ambiguities.get("ssid_network", []):
        questions.append(
            f"I see that '{term}' is mentioned. Is '{term}' the name of the wireless "
            f"network (SSID) that devices connect to, the name of the network in "
            f"the Meraki dashboard, or both?"
        )
    
    # Handle location ambiguities
    for term in ambiguities.get("location", []):
        questions.append(
            f"I see '{term}' mentioned. Is '{term}' a room number, a building name, "
            f"or something else?"
        )
    
    # Handle device ambiguities
    for term in ambiguities.get("device", []):
        questions.append(
            f"Could you clarify what type of device '{term}' refers to?"
        )
    
    return questions


def find_matching_networks(
    context: QueryContext,
    available_networks: List[Dict[str, Any]],
    match_fuzzy: bool = True
) -> List[Dict[str, Any]]:
    """Find networks that match the context from a list of available networks.
    
    Args:
        context: QueryContext containing extracted information
        available_networks: List of network dictionaries to match against
        match_fuzzy: Whether to use fuzzy matching for identifiers
        
    Returns:
        List of matching network dictionaries
    """
    matches = []
    
    # Combine all potential network identifiers from context
    network_identifiers = (
        context.network_identifiers + 
        context.building_identifiers
    )
    
    if not network_identifiers:
        return matches
    
    for network in available_networks:
        network_name = network.get("name", "").lower()
        network_id = network.get("id", "").lower()
        network_tags = network.get("tags", [])
        if isinstance(network_tags, str):
            network_tags = [network_tags]
        network_tags = [t.lower() for t in network_tags if t]
        
        # Check for direct matches
        for net_id in network_identifiers:
            net_id_lower = net_id.lower()
            # Direct matches
            if (net_id_lower in network_name or 
                net_id_lower in network_id or
                any(net_id_lower in tag for tag in network_tags)):
                if network not in matches:
                    matches.append(network)
                break
            
            # Fuzzy matches if enabled
            if match_fuzzy:
                # For building identifiers like "Building 5" or "School 6",
                # look for variations like "B5", "S6", etc.
                building_match = re.match(r'(?:building|school|site)\s*([0-9]+)', net_id_lower)
                if building_match:
                    building_num = building_match.group(1)
                    patterns = [
                        f"b{building_num}",
                        f"s{building_num}",
                        f"building{building_num}",
                        f"school{building_num}",
                        f"building-{building_num}",
                        f"school-{building_num}"
                    ]
                    for pattern in patterns:
                        if (pattern in network_name or 
                            pattern in network_id or
                            any(pattern in tag for tag in network_tags)):
                            if network not in matches:
                                matches.append(network)
                            break
    
    return matches
