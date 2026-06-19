# Task #49310 Completion Report

> Migration update (2026-06-19): the stack is deployed idempotently to new
> instance `i-02f9968c4d07985a1` at Elastic IP `13.51.76.196`. DNS, TLS and
> final acceptance checks are complete.

Completion date: 2026-06-19

## Status

Complete and operational. The deployment is managed by the idempotent
`setup_wordpress.yml` playbook. A verification rerun completed with
`changed=0` and `failed=0`.

## Deployment

- Platform: Amazon Linux 2023
- Web server: Nginx 1.30.1
- Database: MariaDB 10.11.15
- PHP: PHP 8.2.31 with PHP-FPM and required WordPress extensions
- Website root: `/home/wpadmin/MyWebsiteProject/public`
- Public URL: `https://mlolad.xyz/`

The task wording requests "MySQL 10.6". MySQL does not have a 10.6 release;
this is understood as MariaDB 10.6. Amazon Linux 2023 supplies the newer
compatible MariaDB 10.11 package, which is installed and enabled.

## Configuration Steps

1. Installed and enabled Nginx, MariaDB, PHP-FPM, Certbot, and PHP extensions.
2. Created the `wpadmin` user and `sftp_users` group.
3. Configured an OpenSSH internal-SFTP chroot at `/home/wpadmin`.
4. Created `wordpress_db` and a restricted database user.
5. Installed WordPress and WP-CLI under the required website root.
6. Configured WordPress with canonical HTTPS `home` and `siteurl` values.
7. Installed phpMyAdmin 5.2.3 with cookie authentication.
8. Configured Nginx for PHP-FPM, WordPress routing, and HTTP-to-HTTPS redirect.
9. Installed a Let's Encrypt ECDSA certificate for `mlolad.xyz`.
10. Enabled `certbot-renew.timer` and tested renewal against Let's Encrypt staging.
11. Created one published personal blog post named `About Me` and removed duplicates.

## Security

- SFTP is chrooted and disables forwarding and X11 forwarding.
- `/home/wpadmin` is owned by `root:root` as required by OpenSSH chroot rules.
- phpMyAdmin uses cookie authentication and disallows passwordless database access.
- HTTP redirects permanently to HTTPS.
- Credentials are kept outside the playbook in `credentials.yml`, mode `0600`.
- The shareable credential sheet is `TASK_49310_CREDENTIALS.txt`, mode `0600`.

For a production handoff, rotate all initial test passwords and encrypt
`credentials.yml` with Ansible Vault.

## Acceptance Results

| Check | Result |
| --- | --- |
| Nginx, MariaDB, PHP-FPM, SSH | Active and enabled |
| Nginx configuration test | Passed |
| HTTP redirect | `301` to HTTPS |
| Website | `200` |
| WordPress admin | Redirects to secure login |
| phpMyAdmin | `200` |
| WordPress canonical URLs | HTTPS |
| Published `About Me` posts | Exactly one |
| Database credential login | Passed |
| Chrooted SFTP credential login | Passed |
| Certificate expiry | 2026-09-17 |
| Automated renewal timer | Active and enabled |
| Certbot renewal dry run | Passed |
| Ansible idempotence | `changed=0`, `failed=0` |

## Operation

Run the deployment from `ansible-setup`:

```bash
ansible-playbook setup_wordpress.yml
```
