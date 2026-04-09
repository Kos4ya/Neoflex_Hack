import './IRHeader.css'

enum Role {
  Candidate = 'Кандидат',
  Interviewer = 'Интервьюер'
}

const RoleClass = {
  [Role.Candidate]: 'header__role--candidate',
  [Role.Interviewer]: 'header__role--interviewer'
};

type IRHeaderProps = {
  role: Role,
  name: string
}

export const IRHeader = ( {role, name} : IRHeaderProps) => {
    return (
        <header className="ir-header">
        <div className="ir-header__left">
          <div className="ir-header__logo">
            <img src='src/assets/Icons/logo.svg'/>
            <span className="ir-header__logo-text">NeoCodeBoad feat Pukeko</span>
          </div>
          <span className="ir-header__sep" />
          <span className={`ir-header__role ${RoleClass[role]}`}>{role}</span>
        </div>
        <div className="ir-header__right">
          <div className="ir-header__info">
            <span className="ir-header__status-dot" />
            <span>{role === Role.Candidate ? Role.Interviewer : Role.Candidate}</span>
            <span className="ir-header__name">{name}</span>
          </div>
        </div>
      </header>
    )
}