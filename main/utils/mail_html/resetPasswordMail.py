def resetPasswordMail(last_name, first_name, encrypted_mail, url):
    return '''
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <title>Verify Email Address</title>
  <style>

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }

    @keyframes ping {

      75%,
      100% {
        transform: scale(2);
        opacity: 0;
      }
    }

    @keyframes pulse {
      50% {
        opacity: .5;
      }
    }

    @keyframes bounce {

      0%,
      100% {
        transform: translateY(-25%);
        animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
      }

      50% {
        transform: none;
        animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
      }
    }

    @media (max-width: 600px) {
      .sm-leading-32 {
        line-height: 32px !important;
      }

      .sm-px-24 {
        padding-left: 24px !important;
        padding-right: 24px !important;
      }

      .sm-py-32 {
        padding-top: 32px !important;
        padding-bottom: 32px !important;
      }

      .sm-w-full {
        width: 100% !important;
      }
    }

  </style>
</head>
''' + '''
<body
  style="margin: 0; padding: 0; width: 100%; word-break: break-word; -webkit-font-smoothing: antialiased; --bg-opacity: 1; background-color: #eceff1; background-color: rgb(236, 239, 241);"
  bis_register="W3sibWFzdGVyIjp0cnVlLCJleHRlbnNpb25JZCI6ImVwcGlvY2VtaG1ubGJoanBsY2drb2ZjaWllZ29tY29uIiwiYWRibG9ja2VyU3RhdHVzIjp7IkRJU1BMQVkiOiJlbmFibGVkIiwiRkFDRUJPT0siOiJlbmFibGVkIiwiVFdJVFRFUiI6ImVuYWJsZWQiLCJSRURESVQiOiJkaXNhYmxlZCJ9LCJ2ZXJzaW9uIjoiMS45LjAiLCJzY29yZSI6MTA5MDAwfV0=">
  <div style="display: none;" bis_skin_checked="1">Please verify your email address</div>
  <div role="article" aria-roledescription="email" aria-label="Verify Email Address" lang="en" bis_skin_checked="1">
    <table style=" width: 100%;" width="100%"
      cellpadding="0" cellspacing="0" role="presentation">
      <tbody>
        <tr>
          <td align="center"
            style="--bg-opacity: 1; background-color: #eceff1; background-color: rgb(236, 239, 241); "
            bgcolor="rgb(236, 239, 241)">
            <table class="sm-w-full" style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; width: 600px;"
              width="600" cellpadding="0" cellspacing="0" role="presentation">
              <tbody>
                <tr>
                  <td align="center" class="sm-px-24" style="font-family: &#39;Montserrat&#39;,Arial,sans-serif;">
                    <table style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; width: 100%;" width="100%"
                      cellpadding="0" cellspacing="0" role="presentation">
                      <tbody>
                        <tr>
                          <td class="sm-px-24"
                            style="--bg-opacity: 1; background-color: #ffffff; background-color: rgb(255, 255, 255); border-radius: 4px;  font-size: 14px; line-height: 24px; padding: 48px; text-align: left;  color: #626262; color: rgb(98, 98, 98);"
                            bgcolor="rgb(255, 255, 255)" align="left">
                            <p style="font-weight: 600; font-size: 18px; margin-bottom: 0;">Сайн байнa уу</p>
                            <p
                              style="font-weight: 700; font-size: 20px; margin-top: 0;  color: #ff5850; color: rgb(255, 88, 80);">
                              {} {}!</p>
                            <p class="sm-leading-32"
                              style="font-weight: 600; font-size: 20px; margin: 0 0 16px;  color: #263238; color: rgb(38, 50, 56);">
                              Нууц үг солих! 👋
                            </p>
                            <p style="margin: 0 0 24px;">
                              Нууц үг солих товч дээр дарж нууц үгээ солино уу. Энэхүү нууц үг солих мэйл нь 15 минут хүчинтэйг анхаарна уу.
                            </p>
                            <p style="margin: 0 0 24px;">
                              Хэрэв та нууц үгээ солих үйлдэл хийгээгүй бол энэ имэйлийг үл тоомсорлож болно.
                            </p>
                            <table style="font-family: &#39;Montserrat&#39;,Arial,sans-serif;" cellpadding="0"
                              cellspacing="0" role="presentation">
                              <tbody>
                                <tr>
                                  <td
                                    style="mso-padding-alt: 16px 24px; --bg-opacity: 1; background-color: #7367f0; background-color: rgb(115, 103, 240); border-radius: 4px; "
                                    bgcolor="rgb(115, 103, 240)">
                                    <a href='{}/account/forgot-password-change-pass/?token={}'
                                      style="display: block; font-weight: 600; font-size: 14px; line-height: 100%; padding: 16px 24px;  color: #ffffff; color: rgb(255, 255, 255); ">Нууц үг солих</a>
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                            <table style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; width: 100%;" width="100%"
                              cellpadding="0" cellspacing="0" role="presentation">
                              <tbody>
                                <tr>
                                  <td
                                    style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; padding-top: 32px; padding-bottom: 32px;">
                                    <div
                                      style="--bg-opacity: 1; background-color: #eceff1; background-color: rgb(236, 239, 241); height: 1px; line-height: 1px;"
                                      bis_skin_checked="1">‌</div>
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                            <p style="margin: 0 0 16px;">Баярлалаа, <br>HR Хүний нөөцийн систем</p>
                          </td>
                        </tr>
                        <tr>
                          <td style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; height: 20px;" height="20">
                          </td>
                        </tr>
                        <tr>
                          <td style="font-family: &#39;Montserrat&#39;,Arial,sans-serif; height: 16px;" height="16">
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</body>

</html>
    '''.format(last_name, first_name, url, encrypted_mail)
