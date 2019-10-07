// Config
const unrenPath = './../UnRen.bat';
const buildDest = './UnRen.bat';
const tmpPath = './tmp/';
// End Config

const { exec } = require('child_process');
const nodegit = require('nodegit');
const fse = require('fs-extra');
const path = require('path');

const gitClone = opts => {
	let gitPath = path.resolve(tmpPath, opts.tmpGit);
	let cloneOptions = new nodegit.CloneOptions();

	if ('branch' in opts) {
		cloneOptions.checkoutBranch = opts.branch; 
	}

	console.log('Removing "' + gitPath + '" ...');

	fse.remove(gitPath).then(() => {
		console.log('Cloning "' + opts.url + '" to "' + gitPath + '" ...');

		nodegit.Clone(opts.url, gitPath, cloneOptions).then(repo => {
			return repo.getHeadCommit();
		})
		.done(commit => {
			opts.callback(commit, gitPath);
		});
	});
};

const encodeSplit = (name, filePath) => {
	let srcBase = '';
	let srcMerge = '';
	let chunks = fse.readFileSync(filePath, { encoding: 'base64' }).split(/(.{4864})/).filter(O=>O);

	chunks.forEach((str, k) => {
		let num = String(k+1).padStart(2, 0);
		srcBase += 'set ' + name + num + '=' + str + '\r\n';
		srcMerge += 'echo %' + name + num + '%>> "%' + name + '%.tmp"\r\n';
	});

	return { base: srcBase, merge: srcMerge };
};

if (fse.existsSync(buildDest)) {
	console.error('Error: The build destination already exists - "' + buildDest + '"');
	process.exit(1);
}

let unrenSrc = fse.readFileSync(unrenPath, 'utf8');

gitClone({
	url: 'https://github.com/F95Sam/unrpyc',
	tmpGit: 'unrpyc',
//	branch: 'tag_bypass',
	callback: (commit, repoPath) => {
		let cabFolder = path.resolve(repoPath, 'decompiler/');
		let filesPath = path.resolve(repoPath, 'files.txt');

		fse.renameSync(path.resolve(repoPath, 'unrpyc.py'), path.resolve(cabFolder, 'unrpyc.py'));

		exec('dir /s /b /a-d "' + cabFolder + '" >"' + filesPath + '"', (err, stdout, stderr) => {
			if (err) {
				return console.error(err);
			}

			console.log('Compressing to unrpy.cab ...');

			exec('makecab /V1 /D "CabinetName1=_unrpyc.cab" /F "' + filesPath + '"', { cwd: repoPath }, (err, stdout, stderr) => {
				if (err) {
					return console.error(err);
				}

				console.log(stdout);
				console.log('Encoding with base64 and splitting ...');

				let src = encodeSplit('unrpyccab', path.resolve(repoPath, 'disk1/', '_unrpyc.cab'));
				unrenSrc = unrenSrc.replace(/\[UNRPYC\/\/SHA\]/g, commit.sha().substr(0, 7));
				unrenSrc = unrenSrc.replace(/\[UNRPYC\/\/DATE\]/g, new Date(commit.date()).toISOString());
				unrenSrc = unrenSrc.replace(/\[UNRPYC\/\/BASE\]\s+/, src.base);
				unrenSrc = unrenSrc.replace(/\[UNRPYC\/\/MERGE\]\s+/, src.merge);

				gitClone({
					url: 'https://github.com/Shizmob/rpatool',
					tmpGit: 'rpatool',
					callback: (commit, repoPath) => {
						console.log('Encoding with base64 and splitting ...');

						let src = encodeSplit('rpatool', path.resolve(repoPath, 'rpatool'));
						unrenSrc = unrenSrc.replace(/\[RPATOOL\/\/SHA\]/g, commit.sha().substr(0, 7));
						unrenSrc = unrenSrc.replace(/\[RPATOOL\/\/DATE\]/g, new Date(commit.date()).toISOString());
						unrenSrc = unrenSrc.replace(/\[RPATOOL\/\/BASE\]\s+/, src.base);
						unrenSrc = unrenSrc.replace(/\[RPATOOL\/\/MERGE\]\s+/, src.merge);

						let date = new Date();
						unrenSrc = unrenSrc.replace(/^REM\s+\[DEV\/\/WARN_START.*?DEV\/\/WARN_END\]\s+/ms, '');
						unrenSrc = unrenSrc.replace(/\[DEV\/\/BUILD_DATE\]/, date.getFullYear().toString().substr(-2) + String(date.getMonth() + 1).padStart(2, 0) + String(date.getDate()).padStart(2, 0));

						console.log('Writing built file ...');
						fse.writeFileSync(buildDest, unrenSrc);

						console.log('\nFinished!');
					}
				});
			});
		});
	}
});
