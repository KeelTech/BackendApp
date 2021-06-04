import React from 'react'
import { Link, useRouteMatch } from 'react-router-dom'

import styles from './NavigationBar.module.scss'
import UploadTemplateKitButton from '../Buttons/UploadTemplateKitButton'

const NavigationBar = () => {
  return (
    <div className={styles.wrapper}>
      <div className={styles.logo}>
        <Link to='/' className={styles.logoLink}>
          Envato
        </Link>
      </div>

      <nav className={styles.menu}>
        <ul className={styles.menuInner}>
          <li
            className={styles.menuItem}
          >
            <Link
              to='/template-kits/installed-kits'
              className={`${styles.menuLink} ${useRouteMatch({ path: '/template-kits' }) ? styles.menuLinkActive : ''}`}
            >
              Template Kits
            </Link>

          </li>
        </ul>

        <ul className={`${styles.menuInner} ${styles.menuRight}`}>
          <li className={styles.menuItem}>
            <UploadTemplateKitButton />
          </li>
        </ul>
      </nav>
    </div>
  )
}

export default NavigationBar
