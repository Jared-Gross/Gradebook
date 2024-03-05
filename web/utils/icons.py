import os


class Icons:
    app_icon: str = f"{os.getcwd()}/ui/icons/icon.png"
    female1: str = f"{os.getcwd()}/ui/icons/female1.png"
    female2: str = f"{os.getcwd()}/ui/icons/female2.png"
    female3: str = f"{os.getcwd()}/ui/icons/female3.png"
    female4: str = f"{os.getcwd()}/ui/icons/female4.png"
    male1: str = f"{os.getcwd()}/ui/icons/male1.png"
    male2: str = f"{os.getcwd()}/ui/icons/male2.png"
    male3: str = f"{os.getcwd()}/ui/icons/male3.png"
    male4: str = f"{os.getcwd()}/ui/icons/male4.png"
    male_icons: list[str] = [male1, male2, male3, male4]
    female_icons: list[str] = [
        female1,
        female2,
        female3,
        female4,
    ]
