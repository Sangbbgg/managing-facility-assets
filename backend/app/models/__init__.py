from app.core.database import Base
from app.models.master import (
    LocationNode, GroupNode, EquipmentType,
    OsCatalog, AntivirusCatalog, Department, Person,
)
from app.models.asset import Asset, AssetCodeSequence, AssetChangeLog
from app.models.hw_info import (
    AssetHwSystem, AssetHwCpu, AssetHwMemory,
    AssetHwDisk, AssetHwGpu, AssetHwNic,
)
from app.models.sw_info import AssetSwProduct, AssetSwHotfix, AssetSwProcess
from app.models.custom_field import AssetCustomField
from app.models.layout import ColumnLayout
from app.models.collect_script import CollectScript
from app.models.record import (
    InspectionRecord, EventLogRecord, ConsoleAccessRecord,
    SealRecord, PasswordRecord,
)
from app.models.form_template import ReportFormTemplate, ReportFormMapping  # v3
from app.models.report import ReportJob
