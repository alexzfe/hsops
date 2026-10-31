# Observability

What could fail today without the user finding out?

Go through these failures and, for each one, name the check that would alert the user, or state that nothing would:

- a container down
- the whole server down (a monitor on the server itself can't report this)
- a disk above 85%
- a SMART warning
- a degraded pool, or a failed scrub
- a backup that hasn't run
- a certificate about to expire
- the Tailscale node key expiring.

Then check that the alerts would actually be seen:

- alerts reach a channel the user reads
- the profile's Monitoring section matches what is actually running
- the logs are kept long enough to diagnose last week's problem.
