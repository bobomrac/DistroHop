<h1 align="center">🐧 DistroHop</h1>
<h3 align="center">Bring your files + configs + apps → To any Linux distro</strong><br>
  Supports Debian/Ubuntu • Fedora/RHEL • Arch • Derivatives</h3>

<div align="center">
NOTE: This is a simple tool to make changing distro a little quicker.
<br>It's not meant to be a complete migration tool.
</div>
<br>

<h2>✨ Features</h2>
<ul>
  <li>📦 Backs up home files and .config files (Documents, configs, etc.)</li>
  <li>📋 Saves your installed apps as a list (APT/DNF/Pacman/Flatpak)</li>
  <li>🔄 Restores apps automatic using your new distro's package manager and flatpak</li>
  <li>💾 Creates single-file USB backups</li>
</ul>

<h2>🔧 Usage</h2>
<h3>Export Backup</h3>
<ol>
  <li>Insert USB → Select files/apps → Create backup</li>
</ol>

<h3>Import Restore</h3>
<ol>
  <li>Insert backup USB → Restore files → Reinstall same apps</li>
</ol>

<h2>📌 Supported Systems</h2>
<table>
  <tr>
    <th>Package Manager</th>
    <th>Distros</th>
  </tr>
  <tr>
    <td>APT</td>
    <td>Debian, Ubuntu</td>
  </tr>
  <tr>
    <td>DNF/Yum</td>
    <td>Fedora, RHEL</td>
  </tr>
  <tr>
    <td>Pacman</td>
    <td>Arch, Manjaro</td>
  </tr>
  <tr>
    <td>Flatpak</td>
    <td></td>
  </tr>
</table>

<h2>⚠️ Notes</h2>
<ul>
  <li>Requires Python 3.6+ and basic CLI tools</li>
  <li>Root access needed for app installation</li>
  <li>Package names must match between distros</li>
</ul>
