import base64
from typing import List, Optional

DEFAULT_MESSAGE_SEGMENTS: List[str] = ["MSH", "EVN", "PID", "PD1", "PV1"]


def generate_b64_message(
    adt_type: str,
    ctrl_id: str,
    mrn: str,
    nhs_number: str,
    location: str,
    epr_encounter_id: str,
    include_message_segments: Optional[List] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    dob: Optional[str] = None,
    sex: Optional[str] = None,
    admit_datetime: Optional[str] = None,
    discharge_datetime: Optional[str] = None,
) -> str:

    first_name = first_name if first_name is not None else "Ben"
    last_name = last_name if last_name is not None else "Be-Healthy"
    admit_datetime = admit_datetime if admit_datetime is not None else "20200101121500"
    discharge_datetime = discharge_datetime or ""
    dob = dob or "19821103"
    sex = sex or "1"
    default_msg_segments = {
        "MSH": f"MSH|^~\&|c0481|OXON|OXON_TIE_ADT|OXON|20170731141348||ADT^{adt_type}|{ctrl_id}|P|2.3||||||8859/1",
        "EVN": 'EVN|A01|20170731141300|||RBFTHIRKELLS2^Thirkell^Stephen^^^^^^""^PRSNL^^^ORGDR^""',
        "PID": f'PID|1|{mrn}^^^NOC-MRN^MRN^""|{mrn}^^^NOC-MRN^MRN^RTH_MPI~{nhs_number}^^^NHSNBR^NHSNMBR||{last_name}^{first_name}^^^^^CURRENT||{dob}|{sex}||""|Churchill Hospital^Old Road^OXFORD^""^OX3 7LE^GBR^HOME^Headington^""^^^^^^^^""||||""|""|""|904785488^^^NOC-Encntr Number^FINNBR^""||||C||""||""|""|""||""',
        "PD1": 'PD1|||BE-HEALTHY HEALTH CENTRE (OXFORD)^^K84026|G8404231^CHIVERS^ANDY^ABDUS^^^^""^EXTID',
        "PV1": f'PV1|1|INPATIENT|{location}^NOC^^BED^Musc|22||""^""^""^""^^^""|C1524970^Burge^Peter^Denis^^Mr^^^NHSCONSULTNBR^PRSNL^^^NONGP^""~333798103037^Burge^Peter^Denis^^Mr^^^DRNBR^PRSNL^^^ORGDR^""|testconsultant^Test^Test^^^^^^""^PRSNL^^^ORGDR^""||110|""|""|""|19|""|""||INPATIENT|{epr_encounter_id}^^""^NOC-Attendance^VISITID|""||""||||||||||||||""|""|""|NOC||ACTIVE|||{admit_datetime}|{discharge_datetime}',
    }
    if include_message_segments is None:
        include_message_segments = DEFAULT_MESSAGE_SEGMENTS
    raw_msg = "\n".join([default_msg_segments[seg] for seg in include_message_segments])
    return base64.b64encode(raw_msg.encode("utf8")).decode("utf-8")
