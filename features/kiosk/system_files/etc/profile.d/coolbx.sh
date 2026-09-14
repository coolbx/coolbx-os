# Coolbx OS: zelfde XDG_DATA_DIRS-uitbreiding als /usr/lib/environment.d/50-coolbx.conf (login-shells).
case ":${XDG_DATA_DIRS:-}:" in
  *:/var/lib/coolbx/share:*) ;;
  *) export XDG_DATA_DIRS="/var/lib/coolbx/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}" ;;
esac
