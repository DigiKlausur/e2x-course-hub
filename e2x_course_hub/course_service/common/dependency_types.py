from typing import Annotated

from fastapi import Depends
from jupyterhub_fastapi_adapter.dependencies import User, require_authenticated_user
from sqlalchemy.orm import Session

from ...api.course_api import CourseAPI
from ...api.infrastructure_api import InfrastructureAPI
from ...api.membership_api import MembershipAPI
from ...api.profile_api import ProfileAPI
from .dependencies import (
    get_course_api,
    get_db_session,
    get_infrastructure_api,
    get_membership_api,
    get_profile_api,
)

CurrentUser = Annotated[User, Depends(require_authenticated_user)]
DBSession = Annotated[Session, Depends(get_db_session)]
CourseAPIDep = Annotated[CourseAPI, Depends(get_course_api)]
MembershipAPIDep = Annotated[MembershipAPI, Depends(get_membership_api)]
InfrastructureAPIDep = Annotated[InfrastructureAPI, Depends(get_infrastructure_api)]
ProfileAPIDep = Annotated[ProfileAPI, Depends(get_profile_api)]
