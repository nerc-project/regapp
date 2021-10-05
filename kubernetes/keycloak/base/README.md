# Manual Changes after Keycloak Operator Deploy

* IdP attribute mapping
  * Need to manually add IdP mapper for idp_name to cilogon_idp_name user attribute
  * Manifest defines user attribute mapper but this has not been tested
    * maps cilogon_idp_name user attribute to claim
* Client (service) account roles
  * Service account needs to be able to manage users 
  * Unable to set this in the manifest
  * Client -> regapp -> Service Account Roles -> realm-management
    * Select and add all for now
    * Likely need to tighten up
  * Should probably be implemented as a job

# Notes

* Operator External database implemented as headless service with "External" type
  * service name is keycloak-postgresql
  * woe to those who might name another headless service that...
