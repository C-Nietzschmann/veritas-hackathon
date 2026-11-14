# Credits

Hackathon rule: public datasets, open-source libraries and pre-trained models are allowed as long as they are credited. Add a row the moment you first use something. Owner: Data and evaluation lead.

## Datasets
| Name | Link | Licence | Used for |
|---|---|---|---|
| Companies House public data API | https://developer.company-information.service.gov.uk/ | Crown copyright. Companies House says: "We impose no rules or requirements on how the information on the public register is used" ([Companies House data products](https://www.gov.uk/guidance/companies-house-data-products)). Checked 14 Nov: the API has no separate licence. Rate limit: 600 requests per 5 minutes per key ([developer guidelines](https://developer.company-information.service.gov.uk/developer-guidelines)). The same page says users must follow data protection and copyright law, which is why names, birth dates and postcodes are masked in every output (#49). | Company profiles, insolvency cases and officer lists of UK construction companies: the raw data behind the mentions, the claims and the failure label |

## Pre-trained models
| Name | Link | Licence | Used for |
|---|---|---|---|
| | | | |

## Libraries
The usual ones (numpy, pandas, scikit-learn, PyTorch and so on) are listed in `requirements.txt`. List here anything unusual or central to the project.

| Name | Link | Used for |
|---|---|---|
| numpy | https://numpy.org | Numbers and the fixed random seed |
| pandas | https://pandas.pydata.org | Every table: mentions, claims, pairs, links, decisions |
| scikit-learn | https://scikit-learn.org | The matcher (logistic regression, `src/resolve.py`) |
| matplotlib | https://matplotlib.org | The evidence graph and the notebook's figures |
| requests | https://requests.readthedocs.io | Calls to the Companies House API in the crawler |
| python-dotenv | https://github.com/theskumar/python-dotenv | Reads each person's API key from a local `.env` file, never from git |
| ipywidgets | https://github.com/jupyter-widgets/ipywidgets | The cost sliders and Reset button in the notebook's Demo (#104). Agreed on the team call before adding it. |
| Jupyter | https://jupyter.org | Runs `notebooks/main.ipynb` locally |
| pytest | https://pytest.org | The tests in `tests/`, run on every push |

## Code and ideas from elsewhere
Tutorials, papers, or snippets we adapted. Link and one line on what we took.
- Chow's rule for when to abstain: C. K. Chow, "On optimum recognition error and reject tradeoff", IEEE Transactions on Information Theory 16(1), 1970. We used it to turn the three costs into the CLEAR and FLAG thresholds (`decide.thresholds`, ADR-004).
- Companies House `api-enumerations` (https://github.com/companieshouse/api-enumerations): its `constants.yml` list, used to check the insolvency case types and date types the adapter counts.
- The Wilson score interval: E. B. Wilson, "Probable inference, the law of succession, and statistical inference", Journal of the American Statistical Association 22(158), 1927. We used it for the 95% intervals around failure rates and calibration shares (`real_slice.wilson`, card #36).

## AI tools
Which assistants we used and what for. Summarised from the "AI used for" lines in `Log/`.
- **Claude (claude.ai, Anthropic)**: drafted the plan, decisions and cards from our concept; wrote code and tests at our request (schema, tiny world, as-of view, baselines, scoring, decision-layer fixes); reviewed pull requests and drafted review comments and "How it works" notes.
- **Claude Code (Anthropic), models Claude Opus 5.5 and Claude Fable 5.2**: wrote code and tests at our request (crawler, adapter fixes, label, masking, name guard, interface, what-if and sliders), ran the crawl and the notebook, checked API facts on the web, opened and merged our pull requests after we read the code, and drafted log entries.
- Our rules for AI help: a team member reads the code before it is merged, the task's owner confirms its "How it works" note, and every number in Evaluation comes from code that was run, never from an AI's guess.
