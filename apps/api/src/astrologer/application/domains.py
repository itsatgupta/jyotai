"""NEXT-WEALTH-01: the domain registry.

Each answered domain has one :class:`~astrologer.application.domain_pipeline.DomainConfig`:
its houses (whose lords are the domain lords), kārakas, signification tag and composer.

* **Career** (``composer="career"``): the 10th house and the Career signification tag; its
  answer is the reviewed Career composer (reviewed natal rules, reviewed timing rules, the
  year glance, Period themes, comparisons), which reads the tag from this config.
* **Marriage**, **Wealth** and (NEXT-PROPERTY-01) **Property** (``composer="generic"``): the
  generic domain pipeline.

Every other domain keeps the natal contextual answer (``application.detailed_answer``).
"""

from typing import Final

from astrologer.application.domain_pipeline import DomainConfig
from astrologer.application.marriage import MARRIAGE_DOMAIN
from astrologer.application.property import PROPERTY_DOMAIN
from astrologer.application.wealth import WEALTH_DOMAIN
from astrologer.knowledge.models import JyotishDomain
from astrologer.questions.models import QuestionDomain

CAREER_DOMAIN: Final = DomainConfig(
    domain=QuestionDomain.CAREER,
    tag_domain=JyotishDomain.CAREER,
    answer_version="career-answer-v1",
    houses=(10,),
    karakas=(),
    composer="career",
)

DOMAIN_CONFIGS: Final[dict[QuestionDomain, DomainConfig]] = {
    config.domain: config
    for config in (CAREER_DOMAIN, MARRIAGE_DOMAIN, WEALTH_DOMAIN, PROPERTY_DOMAIN)
}


def domain_config(domain: QuestionDomain) -> DomainConfig | None:
    """The registered configuration of ``domain``, or None (natal contextual answer only)."""
    return DOMAIN_CONFIGS.get(domain)
