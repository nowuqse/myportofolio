from rest_framework.permissions import BasePermission, SAFE_METHODS


# Mengizinkan akses baca untuk semua orang dan perubahan hanya untuk pemilik.
class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    # Memeriksa method aman atau status superuser sebagai pemilik portofolio.
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )

# Mengizinkan Editor memperbarui data tanpa hak membuat atau menghapusnya.
class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    # Menentukan izin berdasarkan method, autentikasi, dan peran pengguna.
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
