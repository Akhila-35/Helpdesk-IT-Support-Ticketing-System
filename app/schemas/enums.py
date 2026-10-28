from enum import Enum
class UserRole(str,Enum): ADMIN='admin'; ENGINEER='engineer'; REQUESTER='requester'
class Priority(str,Enum): LOW='low'; MEDIUM='medium'; HIGH='high'; CRITICAL='critical'
class TicketStatus(str,Enum): OPEN='open'; ASSIGNED='assigned'; IN_PROGRESS='in_progress'; WAITING_FOR_USER='waiting_for_user'; RESOLVED='resolved'; CLOSED='closed'
