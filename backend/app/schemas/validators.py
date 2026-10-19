import re

from email_validator import EmailNotValidError, validate_email


NICKNAME_PATTERN = re.compile(r"^[가-힣A-Za-z0-9_]+$")


def normalize_email(value: str) -> str:
    candidate = value.strip()
    try:
        normalized = validate_email(candidate, check_deliverability=False).normalized
    except EmailNotValidError as error:
        raise ValueError("올바른 이메일 주소를 입력해 주세요.") from error
    return normalized.lower()


def validate_password(value: str) -> str:
    if not 8 <= len(value) <= 64:
        raise ValueError("비밀번호는 8~64자로 입력해 주세요.")
    return value


def normalize_nickname(value: str) -> str:
    candidate = value.strip()
    if not 2 <= len(candidate) <= 20:
        raise ValueError("닉네임은 2~20자로 입력해 주세요.")
    if not NICKNAME_PATTERN.fullmatch(candidate):
        raise ValueError("닉네임은 한글, 영문, 숫자, 밑줄만 사용할 수 있습니다.")
    return candidate
