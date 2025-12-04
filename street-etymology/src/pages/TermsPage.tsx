import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export function TermsPage() {
  return (
    <div className="min-h-screen bg-stone-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm mb-8">
          <Link to="/" className="text-stone-500 hover:text-stone-700">Home</Link>
          <ChevronRight className="w-4 h-4 text-stone-400" />
          <span className="text-stone-800 font-medium">Terms of Service</span>
        </nav>

        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8 md:p-12">
          <h1 className="text-3xl font-serif font-bold text-stone-800 mb-2">
            Terms of Service
          </h1>
          <p className="text-stone-600 mb-8">
            Last updated: December 2024
          </p>

          <div className="prose prose-stone max-w-none">
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using Street Etymology UK ("the Service"), you agree to be 
              bound by these Terms of Service. If you do not agree to these terms, please 
              do not use the Service.
            </p>

            <h2>2. Description of Service</h2>
            <p>
              Street Etymology UK provides an online platform for researching, sharing, 
              and discovering the etymological origins of UK street names. The Service 
              includes a searchable database, interactive maps, and community contribution 
              features.
            </p>

            <h2>3. User Accounts</h2>
            <h3>3.1 Registration</h3>
            <p>
              Some features require account registration. You must provide accurate and 
              complete information and keep your account details up to date.
            </p>

            <h3>3.2 Account Security</h3>
            <p>
              You are responsible for maintaining the confidentiality of your password 
              and for all activities under your account. Notify us immediately of any 
              unauthorised access.
            </p>

            <h3>3.3 Account Termination</h3>
            <p>
              We reserve the right to suspend or terminate accounts that violate these 
              terms or for any other reason at our discretion.
            </p>

            <h2>4. User Contributions</h2>
            <h3>4.1 Contribution Guidelines</h3>
            <p>By submitting etymology contributions, you agree that:</p>
            <ul>
              <li>Your contributions are accurate to the best of your knowledge</li>
              <li>You have the right to share the information provided</li>
              <li>Your contributions do not infringe on any intellectual property rights</li>
              <li>Your contributions comply with applicable laws</li>
            </ul>

            <h3>4.2 Licence Grant</h3>
            <p>
              By submitting contributions, you grant Street Etymology UK a non-exclusive, 
              worldwide, royalty-free licence to use, reproduce, modify, and display your 
              contributions as part of the Service.
            </p>

            <h3>4.3 Moderation</h3>
            <p>
              All contributions are subject to moderation. We reserve the right to reject, 
              edit, or remove any contribution without notice.
            </p>

            <h2>5. Intellectual Property</h2>
            <h3>5.1 Our Content</h3>
            <p>
              The Service and its original content (excluding user contributions) are 
              protected by copyright, trademark, and other intellectual property laws. 
              You may not reproduce, distribute, or create derivative works without our 
              prior written permission.
            </p>

            <h3>5.2 Data Use</h3>
            <p>
              Etymology data may be exported for personal, educational, or research 
              purposes with proper attribution. Commercial use requires prior written 
              permission.
            </p>

            <h2>6. Prohibited Conduct</h2>
            <p>You agree not to:</p>
            <ul>
              <li>Use the Service for any unlawful purpose</li>
              <li>Submit false, misleading, or defamatory content</li>
              <li>Impersonate any person or entity</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Attempt to gain unauthorised access to any part of the Service</li>
              <li>Use automated systems to scrape or collect data without permission</li>
              <li>Harass or harm other users</li>
            </ul>

            <h2>7. Disclaimer of Warranties</h2>
            <p>
              The Service is provided "as is" without warranties of any kind. We do not 
              guarantee the accuracy, completeness, or reliability of any etymology 
              information. While we strive for accuracy, street name etymologies may be 
              subject to scholarly debate.
            </p>

            <h2>8. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, Street Etymology UK shall not be 
              liable for any indirect, incidental, special, consequential, or punitive 
              damages arising from your use of the Service.
            </p>

            <h2>9. Indemnification</h2>
            <p>
              You agree to indemnify and hold harmless Street Etymology UK from any 
              claims, damages, or expenses arising from your use of the Service or 
              violation of these terms.
            </p>

            <h2>10. Third-Party Links</h2>
            <p>
              The Service may contain links to third-party websites. We are not responsible 
              for the content or practices of these sites.
            </p>

            <h2>11. Modifications</h2>
            <p>
              We may modify these Terms at any time. Continued use of the Service after 
              changes constitutes acceptance of the modified Terms.
            </p>

            <h2>12. Governing Law</h2>
            <p>
              These Terms shall be governed by the laws of England and Wales. Any disputes 
              shall be subject to the exclusive jurisdiction of the courts of England and Wales.
            </p>

            <h2>13. Severability</h2>
            <p>
              If any provision of these Terms is found unenforceable, the remaining 
              provisions shall continue in effect.
            </p>

            <h2>14. Contact</h2>
            <p>
              For questions about these Terms, please contact us at:
            </p>
            <p>
              <strong>Email:</strong> legal@streetetymology.co.uk
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
