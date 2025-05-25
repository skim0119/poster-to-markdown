POSTER_PROMPT = """This is a research poster. Provide a markdown summary with:

#<tag1> #<tag2> #<tag3>
choose from:
    topic/soft-robot,
    topic/multi-agent,
    topic/reinforcement-learning,
    topic/immitation-learning,
    topic/manipulation,
    topic/HRI,
    topic/EMG/EEG/EMG/MEG,
    topic/unknown
Always add: #poster #ICRA2025

Search Strategy for Finding Related Papers:
1. First, search using Author's name and the poster title, breaking it into key technical terms
2. Search for maximum 10 papers to save tokens.
3. Include both the arXiv link and DOI if available

Add a section that describes:
- Background of their lab/institution
- Previous work from the authors (especially first and last author)
- Related work from their institution
- Similar work from other institutions

Format it nicely with headers, bullet points, and emphasis where appropriate.

Follow this template structure (DO NOT include the ```markdown and ``` markers in your output):

```markdown
---
tag:
  - <tag1>
  - <tag2>
  ...
---

# <Poster Title>

<Note if poster may contain wrong information. double check: <image_path>>

## Authors
- <Author 1>
- <Author 2>

## Key Findings
<Key Findings>

## Methodology
<Methodology: highlight key words>

## Technical Details
- Implementation: <Implementation details, frameworks, tools used>
- Evaluation: <How they evaluated their work, metrics used>
- Limitations: <Any limitations mentioned or apparent>
- Future Work: <Future work mentioned in the poster>

## Related Work and Previous Work
<Related Work from the lab (last author's)>

## Impact and Applications
- Potential Applications: <Where could this work be applied, if specified in the poster.>
- Industry Relevance: <Any industry connections or potential, if specified in the poster.>
- Broader Impact: <Broader impact on the field, if specified or mentioned in the poster.>

## Few remarks
<Any relation back to my research: soft robot, slender robot, SNN, neuromorphic computing,
 multi-agent RL problem>

# URL
<Arxiv link of the paper for the poster>
<Link of the papers that are related. Give a short comment on why it is included.>
```

!!Do not add arbitrary contents unless it is included from the poster or their website or
  related work!!
!!Provide a formal, non-conversational response. Do not include any conversational phrases or
  suggestions for further assistance.!!
"""

FILENAME_PROMPT = """
Based on the poster content, what would be an appropriate filename, in snake_case, for this
markdown summary? Please provide just the filename without extension. File name should be in
English, 3-5 words max.
"""
