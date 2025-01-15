from uuid import UUID

from pydantic import SecretStr

type ID = int
type PASSWORD_HASH = UUID
type PASSWORD_INPUT = SecretStr
