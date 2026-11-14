# Credits

Hackathon rule: public datasets, open-source libraries and pre-trained models are allowed as long as they are credited. Add a row the moment you first use something. Owner: Data and evaluation lead.

## Datasets
| Name | Link | Licence | Used for |
|---|---|---|---|
| Companies House public data API: company profiles, officer and appointment lists, insolvency records, advanced company search, officer search | https://developer.company-information.service.gov.uk/ | Not the Open Government Licence: the register is published under statute (section 47 of the Copyright, Designs and Patents Act 1988). Companies House says: "We impose no rules or requirements on how the information on the public register is used" ([Companies House data products](https://www.gov.uk/guidance/companies-house-data-products); [FOI disclosure 362](https://assets.publishing.service.gov.uk/media/5a7f6e7f40f0b6230268f75c/Disc_Log_362__Enquiry_regarding_Companies_House_Free_Company_Data_Product-ver0.2.pdf) confirms it is not OGL). Credited as the source. Officer records hold personal data, so every output is masked (#49) | Company profiles, insolvency cases, officer and appointment lists of UK construction companies, and the officers who share a director's name: the raw data behind the mentions, the claims and the failure label (crawler #24, adapter #25) |

## Pre-trained models
| Name | Link | Licence | Used for |
|---|---|---|---|
| | | | |

## Libraries
The usual ones (numpy, pandas, scikit-learn, PyTorch and so on) are listed in `requirements.txt`. List here anything unusual or central to the project.

| Name | Link | Used for |
|---|---|---|
| | | |

## Code and ideas from elsewhere
Tutorials, papers, or snippets we adapted. Link and one line on what we took.
- Companies House `api-enumerations` (https://github.com/companieshouse/api-enumerations): its `constants.yml` list, used to check the insolvency case types and date types the adapter counts.

## AI tools
Which assistants we used and what for. Summarised from the "AI used for" lines in `Log/`.
-
