import React from 'react'
import ExternalLink from '../Buttons/ExternalLink'

import styles from './FooterBar.module.scss'

const FooterBar = () => {
  return (
    <div className={styles.footerBar}>
      <p>
        <strong>Feedback &amp; Support: </strong> If you have any questions or feedback for the team please send an email to{' '}
        <ExternalLink href='mailto:extensions@envato.com' text='extensions@envato.com' />{' | '}
        <ExternalLink href='https://envato.com/privacy?utm_source=extensions&amp;utm_medium=referral&amp;utm_campaign=template_kit_import_footer' text='Privacy Policy' />{' | '}
        <ExternalLink href='https://help.market.envato.com/hc/en-us/sections/360007560992-Template-Kits?utm_source=extensions&amp;utm_medium=referral&amp;utm_campaign=template_kit_import_footer' text='Help' />
      </p>
    </div>
  )
}

export default FooterBar
