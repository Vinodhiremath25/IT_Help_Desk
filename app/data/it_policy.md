# Corporate IT Helpdesk Knowledge Base

## Virtual Private Network (VPN)
- Primary Client: GlobalProtect VPN.
- Portal Address: `vpn.corp.company.com`.
- Common Error "Connection Failed (Gateway Unreachable)": Run `ipconfig /flushdns` in Command Prompt and restart the Palo Alto GlobalProtect service.
- Multi-factor Authentication (MFA) is mandatory on every reconnection.

## Office Wi-Fi Connectivity
- Corporate SSID: `Corp-Secure-WiFi`.
- Authentication: WPA3 Enterprise using corporate domain credentials.
- Guest SSID: `Corp-Guest` (Requires daily sponsor token).
- Fix for IP lease exhaustion: Turn Wi-Fi off and on, or run `ipconfig /renew`.

## Hardware & Peripheral Requests
- Standard Monitor: Dell UltraSharp 27" USB-C Hub Monitor.
- Standard Laptop Refresh Cycle: 3 years for engineering laptops, 4 years for non-technical roles.
- Broken or Damaged Hardware: Open an IT Jira ticket under category `Hardware` with priority `High`. Damaged items must be brought to IT Desk on Floor 2.

## Software Installation & Licensing
- Standard Pre-approved Tools: Slack, VS Code, Zoom, Google Chrome, Postman, Git.
- Restricted Tools (Requires Manager Approval): Docker Desktop, JetBrains All Products Pack, AWS CLI elevated keys.
- Requests for unapproved software must be escalated through an IT ticket under category `Software`.