#!/usr/bin/env python3
"""#235 Linux account-derived init file semantics, limited Boolean fixture model.

This is NOT source-equivalent SCAP 1.4 or OVAL runtime execution. It deliberately
models complete collected populations and transparent selected/file identity;
it does not implement liboval probe traversal or true OVAL entity/status flags.
The project must not adopt the native authoring rewrite merely because this
model returns the expected complete-evidence outcomes.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

TRUE="true"
FALSE="false"
UNKNOWN="unknown"
ERROR="error"
ALLOWED_MODE=0o740  # valid file mode may only SET these permission bits
FLAG_BITS={
    "setuid":0o4000,
    "setgid":0o2000,
    "sticky":0o1000,
    "group_write":0o020,
    "group_execute":0o010,
    "other_read":0o004,
    "other_write":0o002,
    "other_execute":0o001,
}
USER_NAME_REGEX=re.compile(r"[\w]+")
FILENAME_REGEX=re.compile(r"^\.[^\s\.]+")
ALL_FLAGS_MASK=sum(FLAG_BITS.values())
assert ALL_FLAGS_MASK==0o7037,oct(ALL_FLAGS_MASK)
assert ALL_FLAGS_MASK==(0o7777 & ~ALLOWED_MODE)
assert 0o740 & ALL_FLAGS_MASK==0

@dataclass(frozen=True)
class Result:
    result: str
    reason: str
    accounts_selected: int
    files_selected: int

def only_these_bits(mode, allowed_bits):
    """Typed POSIX bit-set comparator; textual allowed mask must be octal.

    A plain numeric <= comparator (even after octal parse) is incorrect.
    """
    if not isinstance(mode,int) or isinstance(mode,bool) or not 0<=mode<=0o7777:
        raise ValueError("file mode must be a numeric POSIX 12-bit mask")
    if not isinstance(allowed_bits,str) or not re.fullmatch(r"[0-7]{4}",allowed_bits):
        raise ValueError("allowed permission bits must be a four-digit octal STRING")
    return (mode & ~int(allowed_bits,8))==0

def mode_complies(mode):
    """Boolean iff all EIGHT OVAL-derived boolean flag constraints are false.

    "no more permissive than 0740" must mean allowed-bit *subset*, never
    ordinary numeric <=, lexical <= or a numeric threshold comparator.
    """
    return only_these_bits(mode,"0740")

def eight_flag_comparisons(mode):
    if not isinstance(mode,int) or isinstance(mode,bool) or not 0<=mode<=0o7777:
        raise ValueError("invalid mode")
    return {key:bool(mode & mask)==False for key,mask in FLAG_BITS.items()}

def _select_account(account,group):
    for needed in ("id","username","uid","home_dir"):
        if needed not in account:
            return UNKNOWN
    if not isinstance(account["uid"],int) or isinstance(account["uid"],bool):
        return ERROR
    if not all(isinstance(account[k],str) for k in ("id","username","home_dir")):
        return ERROR
    if not USER_NAME_REGEX.search(account["username"]):
        return FALSE
    if account["home_dir"]=="/":
        return FALSE
    if group=="root":
        return TRUE if account["uid"]==0 else FALSE
    if group=="non_system":
        return TRUE if account["uid"]>=1000 else FALSE
    raise ValueError("unsupported account category")

def _select_file(file,selected_accounts):
    """Collection provenance already associates a file with a selected account.

    This does NOT implement actual on-disk traversal depth, symlink handling,
    filesystem=all or pathname-matching probe semantics.
    """
    for field in ("id","account_id","directory","name","kind"):
        if field not in file:return UNKNOWN
    if not all(isinstance(file[x],str) for x in ("id","account_id","directory","name","kind")):
        return ERROR
    if file["account_id"] not in selected_accounts:return FALSE
    account=selected_accounts[file["account_id"]]
    if file["directory"]!=account["home_dir"]:
        return FALSE
    if not FILENAME_REGEX.search(file["name"]):
        return FALSE
    return FALSE if file["kind"]=="directory" else TRUE

def evaluate(snapshot,group):
    """A restricted complete/partial source-population model.

    Root existence is GLOBAL across the union of files from every root UID=0
    account, not per-root account. Non-system file test is if_present globally.
    Partial discovery may establish a definitive violation but cannot establish
    missing resource or absence-of-violation.
    """
    if group not in {"root","non_system"}:raise ValueError("unknown group")
    acc_status=snapshot.get("accounts_status")
    file_status=snapshot.get("files_status")
    if acc_status not in {"complete","incomplete","error","not collected"}:
        raise ValueError("explicit accounts_status required")
    if file_status not in {"complete","incomplete","error","not collected"}:
        raise ValueError("explicit files_status required")
    if "error" in (acc_status,file_status):
        return Result(ERROR,"provider acquisition error",0,0)
    if "not collected" in (acc_status,file_status):
        return Result(UNKNOWN,"acquisition not collected",0,0)
    accounts=snapshot.get("accounts",[])
    files=snapshot.get("files",[])
    if not isinstance(accounts,list) or not isinstance(files,list):
        raise ValueError("accounts/files must be lists")
    selected={}
    unknown_accounts=False
    for account in accounts:
        match=_select_account(account,group)
        if match==ERROR:return Result(ERROR,"invalid account evidence",len(selected),0)
        if match==UNKNOWN:
            unknown_accounts=True
            continue
        if match==TRUE:
            if account["id"] in selected:
                return Result(ERROR,"duplicate account id",len(selected),0)
            selected[account["id"]]=account
    chosen={}
    unknown_files=False
    for file in files:
        match=_select_file(file,selected)
        if match==ERROR:return Result(ERROR,"invalid file evidence",len(selected),len(chosen))
        if match==UNKNOWN:
            unknown_files=True
            continue
        if match==TRUE:
            if file["id"] in chosen and chosen[file["id"]]!=file:
                return Result(ERROR,"ambiguous reused file identity",len(selected),len(chosen))
            chosen[file["id"]]=file
    for file in chosen.values():
        if "mode" not in file:
            unknown_files=True
        else:
            try:ok=mode_complies(file["mode"])
            except ValueError:
                return Result(ERROR,"invalid mode evidence",len(selected),len(chosen))
            if not ok:
                return Result(FALSE,"known prohibited permission bit",len(selected),len(chosen))
    finished=(acc_status=="complete" and file_status=="complete"
              and not unknown_accounts and not unknown_files)
    if not finished:
        return Result(UNKNOWN,"incomplete account/file identity or mode evidence",
                      len(selected),len(chosen))
    if group=="root" and not chosen:
        return Result(FALSE,"no qualifying root files across entire selected-account union",
                      len(selected),0)
    return Result(TRUE,"all qualifying files comply and root global cardinality met",
                  len(selected),len(chosen))

def per_user_required_root_files(snapshot):
    """Tempting rewrite: every UID-0 user must have at least one qualifying file.

    Deliberately not source equivalent to a global at_least_one file Test.
    Only evaluate complete snapshots; assertion documents a falsifying case.
    """
    if snapshot["accounts_status"]!="complete" or snapshot["files_status"]!="complete":
        raise ValueError("per-user demonstration requires complete snapshot")
    roots={a["id"]:a for a in snapshot["accounts"] if _select_account(a,"root")==TRUE}
    if not roots:return False
    for ident,account in roots.items():
        matches=[f for f in snapshot["files"] if _select_file(f,{ident:account})==TRUE]
        if not matches or not all(mode_complies(f["mode"]) for f in matches):
            return False
    return True
