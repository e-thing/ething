<?php
	
namespace Ething;
	

	
class Mail
{
	
	protected $ething;
	
	public function __construct(Ething $ething) // Constructeur
	{
		$this->ething = $ething;
	}
	
	public function send($subject,$message = null, $attachments = array()){
		$smtpSettings = $this->ething->config('notification.smtp');
		$mailList = $this->ething->config('notification.emails');
		
		if(empty($smtpSettings)){
			throw new Exception("Mail feature not enable");
		}
		
		if(!isset($smtpSettings['host']) || !isset($smtpSettings['port']) || !isset($smtpSettings['user']) || !isset($smtpSettings['password']) ){
			throw new Exception("invalid notification.smtp config");
		}
		
		if(empty($mailList)){
			return true;
		}
		
		if(!isset($subject))
			$subject = 'notification';
		
		if(empty($message))
			$message = '';
		
		//Create a new PHPMailer instance
		$mail = new \PHPMailer;
		//Tell PHPMailer to use SMTP
		$mail->isSMTP();
		//Enable SMTP debugging
		// 0 = off (for production use)
		// 1 = client messages
		// 2 = client and server messages
		$mail->SMTPDebug = 0;
		//Ask for HTML-friendly debug output
		//$mail->Debugoutput = 'html';
		//Set the hostname of the mail server
		$mail->Host = $smtpSettings['host'];
		// use
		// $mail->Host = gethostbyname('smtp.gmail.com');
		// if your network does not support SMTP over IPv6
		//Set the SMTP port number - 587 for authenticated TLS, a.k.a. RFC4409 SMTP submission
		$mail->Port = $smtpSettings['port'];
		//Set the encryption system to use - ssl (deprecated) or tls
		$mail->SMTPSecure = 'tls';
		//Whether to use SMTP authentication
		$mail->SMTPAuth = true;
		//Username to use for SMTP authentication - use full email address for gmail
		$mail->Username = $smtpSettings['user'];
		//Password to use for SMTP authentication
		$mail->Password = $smtpSettings['password'];
		//Set who the message is to be sent from
		$mail->setFrom($smtpSettings['user'], 'eThing');
		//Set an alternative reply-to address
		//$mail->addReplyTo('replyto@example.com', 'First Last');
		//Set who the message is to be sent to
		foreach($mailList as $email)
			$mail->addAddress($email);
			
		
		if(is_array($attachments) && !empty($attachments)){
			foreach($attachments as $attachment){
				if(is_array($attachment) && isset($attachment['name']) && isset($attachment['content'])){
					$mail->addStringAttachment($attachment['content'], $attachment['name']);
				}
			}
		}
		
		//Set the subject line
		$mail->Subject = '[eThing] '.$subject;
		//set the text body
		$mail->isHTML(true); // accept html
		$mail->Body = $message;
		//send the message, check for errors
		if (!$mail->send()) {
			throw new Exception("Mailer Error: " . $mail->ErrorInfo);
		}
		
		return true;
	}
	

}


